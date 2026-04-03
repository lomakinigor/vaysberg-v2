"""
Генератор стратегического HTML-отчёта.
Принимает данные анкеты → возвращает красивый HTML-отчёт.
"""
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from datetime import datetime
from models import IntakeForm, Finding, AutomationOption
from typing import List, Dict, Any

env = Environment(loader=FileSystemLoader(Path(__file__).parent / "templates"))


# ─── Справочники ────────────────────────────────────────────

BUDGET_LABELS = {
    "none":     "Нет бюджета (только органика)",
    "under30k": "До 30 000 ₽/мес",
    "30-100k":  "30 000 – 100 000 ₽/мес",
    "over100k": "Более 100 000 ₽/мес",
    "private":  "Не раскрывается",
}

GOAL_LABELS = {
    "leads":   "Увеличить заявки / звонки",
    "cpl":     "Снизить стоимость лида (CPL)",
    "segment": "Повысить долю сегмента в выручке",
    "brand":   "Усилить узнаваемость бренда",
    "ltv":     "Повысить LTV и удержание",
    "geo":     "Выйти в новый регион",
    "other":   "Другая цель",
}

CONTENT_LABELS = {
    "nobody":  "Контент не создаётся",
    "owner":   "Руководитель (иногда)",
    "smm":     "SMM-специалист",
    "agency":  "Агентство",
    "other":   "Другое",
}

DISCOVERY_LABELS = {
    "word_of_mouth": "Сарафанное радио",
    "maps":          "Яндекс.Карты / 2ГИС",
    "vk":            "ВКонтакте",
    "yandex_direct": "Яндекс.Директ",
    "instagram":     "Instagram",
    "telegram":      "Telegram",
    "other":         "Другое",
}

ACCESS_LABELS = {
    None:       ("—",        "none"),
    "none":     ("Нет",      "none"),
    "screens":  ("Скриншоты","partial"),
    "readonly": ("Read-only","partial"),
    "full":     ("Полный",   "full"),
}


# ─── Анализ каналов ─────────────────────────────────────────

def _has(val: str | None) -> bool:
    return bool(val and val.strip() and val.strip().lower() not in ("нет", "no", "-", "—"))


def analyze_channels(d: IntakeForm) -> List[Dict]:
    channels = []

    # Сайт
    site_link = d.website or d.ch_site
    channels.append({
        "name":    "Сайт",
        "icon":    "🌐",
        "link":    site_link or "—",
        "status":  "warning" if site_link else "critical",
        "status_label": "Присутствует" if site_link else "Не указан",
        "score":   65 if site_link else 10,
        "findings": [
            {"text": "Сайт найден, базовый аудит запланирован",        "type": "ok"}      if site_link else
            {"text": "Сайт не предоставлен — анализ невозможен",       "type": "critical"},
            {"text": "Мобильная адаптация требует проверки",           "type": "warning"},
            {"text": "PageSpeed и SEO-показатели будут проверены",     "type": "info"},
        ],
    })

    # VK
    vk = d.ch_vk
    channels.append({
        "name":    "ВКонтакте",
        "icon":    "📘",
        "link":    vk or "—",
        "status":  "ok" if _has(vk) else "opportunity",
        "status_label": "Активен" if _has(vk) else "Отсутствует",
        "score":   70 if _has(vk) else 5,
        "findings": [
            {"text": "Сообщество найдено, анализ ER и контента запланирован", "type": "ok"}
            if _has(vk) else
            {"text": "Сообщества VK нет — потеря ~35% аудитории в B2C сегменте", "type": "critical"},
            {"text": "Частота публикаций и вовлечённость будут измерены", "type": "info"},
            {"text": "Анализ рекламных активностей конкурентов в VK",    "type": "info"},
        ],
    })

    # Telegram
    tg = d.ch_tg_channel
    channels.append({
        "name":    "Telegram",
        "icon":    "✈️",
        "link":    tg or "—",
        "status":  "ok" if _has(tg) else "opportunity",
        "status_label": "Активен" if _has(tg) else "Отсутствует",
        "score":   60 if _has(tg) else 5,
        "findings": [
            {"text": "Канал найден, аудиторные метрики запланированы", "type": "ok"}
            if _has(tg) else
            {"text": "Telegram-канал отсутствует — быстрорастущий канал для прогрева", "type": "opportunity"},
            {"text": "Telegram-бот: " + ("настроен" if _has(d.ch_tg_bot) else "не подключён"), "type": "ok" if _has(d.ch_tg_bot) else "warning"},
            {"text": "Роль в воронке продаж будет определена", "type": "info"},
        ],
    })

    # Instagram
    ig = d.ch_instagram
    channels.append({
        "name":    "Instagram",
        "icon":    "📸",
        "link":    ig or "—",
        "status":  "ok" if _has(ig) else "opportunity",
        "status_label": "Активен" if _has(ig) else "Отсутствует",
        "score":   55 if _has(ig) else 5,
        "findings": [
            {"text": "Профиль найден, публичный анализ запланирован", "type": "ok"}
            if _has(ig) else
            {"text": "Instagram отсутствует — ⚠️ недоступен в РФ без VPN", "type": "warning"},
            {"text": "Проверка оформления Bio и CTA", "type": "info"},
        ],
    })

    # Карты
    ymaps = d.ch_ymaps or d.ch_2gis
    channels.append({
        "name":    "Карты / 2ГИС",
        "icon":    "🗺️",
        "link":    ymaps or "—",
        "status":  "ok" if _has(ymaps) else "critical",
        "status_label": "Присутствует" if _has(ymaps) else "Отсутствует",
        "score":   75 if _has(ymaps) else 5,
        "findings": [
            {"text": "Карточка найдена, анализ рейтинга и отзывов запланирован", "type": "ok"}
            if _has(ymaps) else
            {"text": "Карточка отсутствует — упущен тёплый локальный трафик", "type": "critical"},
            {"text": "Проверка актуальности часов работы и фото", "type": "warning"},
            {"text": "Анализ ответов на отзывы конкурентов",      "type": "info"},
        ],
    })

    # Конкуренты
    comps = [n for n in [d.c1_name, d.c2_name, d.c3_name, d.c4_name, d.c5_name] if _has(n)]
    channels.append({
        "name":    "Конкуренты",
        "icon":    "🔍",
        "link":    f"{len(comps)} указано",
        "status":  "ok" if comps else "warning",
        "status_label": f"{len(comps)} конкур." if comps else "Не указаны",
        "score":   80 if len(comps) >= 3 else (50 if comps else 10),
        "findings": [
            {"text": f"Перечислено конкурентов: {len(comps)}", "type": "ok" if comps else "warning"},
            {"text": "Gap-анализ по всем каналам будет проведён", "type": "info"},
            {"text": "Сравнение воронок продаж запланировано",   "type": "info"},
        ],
    })

    return channels


# ─── Находки ────────────────────────────────────────────────

def generate_findings(d: IntakeForm) -> List[Finding]:
    findings = []

    if not _has(d.ch_vk):
        findings.append(Finding(
            channel="ВКонтакте", severity="critical",
            fact="Сообщества VK нет. Это основной канал для 60%+ российской B2C аудитории.",
            recommendation="Создать и оформить сообщество, запустить контент-план на 3 месяца.",
            kpi="500+ подписчиков за 60 дней",
            priority="high", effort="quick_win",
        ))

    if not _has(d.ch_ymaps) and not _has(d.ch_2gis):
        findings.append(Finding(
            channel="Карты", severity="critical",
            fact="Карточка в Яндекс.Картах / 2ГИС отсутствует. Локальный поисковый трафик не привлекается.",
            recommendation="Зарегистрировать и полностью заполнить карточку в обоих сервисах.",
            kpi="Появление в ТОП-3 локальной выдачи за 30 дней",
            priority="high", effort="quick_win",
        ))

    if not _has(d.ch_tg_channel):
        findings.append(Finding(
            channel="Telegram", severity="opportunity",
            fact="Telegram-канал отсутствует. Охват 1000 подписчиков здесь даёт больше контактов, чем 5000 в VK.",
            recommendation="Создать канал, выстроить контент-стратегию вокруг экспертизы.",
            kpi="1000 подписчиков за 90 дней",
            priority="high", effort="strategic",
        ))

    if not _has(d.ch_tg_bot):
        findings.append(Finding(
            channel="Telegram", severity="opportunity",
            fact="Telegram-бот не подключён. Бот автоматизирует первичную квалификацию лидов 24/7.",
            recommendation="Создать бот с FAQ, квалификацией и отправкой заявки в CRM.",
            kpi="Снижение времени ответа с часов до секунд",
            priority="medium", effort="strategic",
        ))

    if d.acc_metrika in (None, "none") and d.acc_ga in (None, "none"):
        findings.append(Finding(
            channel="Сайт", severity="critical",
            fact="Аналитика сайта недоступна. Невозможно понять, откуда приходят клиенты.",
            recommendation="Предоставить read-only доступ к Яндекс.Метрике.",
            kpi="100% покрытие событий целями (заявка, звонок)",
            priority="high", effort="quick_win",
        ))

    if d.budget == "none":
        findings.append(Finding(
            channel="Продвижение", severity="warning",
            fact="Бюджет на продвижение отсутствует. Рост возможен только через органику и удержание.",
            recommendation="Сосредоточиться на SEO, Яндекс.Картах, сарафанном радио, реферальной программе.",
            kpi="20% рост органического трафика за 3 месяца",
            priority="medium", effort="strategic",
        ))

    if d.crm_name in (None, "") or d.crm_name.lower() in ("нет", "no", "—"):
        findings.append(Finding(
            channel="CRM", severity="critical",
            fact="CRM не используется. Заявки и клиенты теряются — нет истории взаимодействий.",
            recommendation="Внедрить AmoCRM или Bitrix24. Первые 14 дней — бесплатно.",
            kpi="0% потерянных заявок, конверсия +15%",
            priority="high", effort="quick_win",
        ))

    comps = [n for n in [d.c1_name, d.c2_name, d.c3_name] if _has(n)]
    if not comps:
        findings.append(Finding(
            channel="Конкуренты", severity="warning",
            fact="Конкуренты не указаны. Без бенчмаркинга сложно определить правильные приоритеты.",
            recommendation="Перечислить 3–5 прямых конкурентов для gap-анализа.",
            kpi="Полный сравнительный анализ каналов",
            priority="medium", effort="quick_win",
        ))

    if d.content_creator in ("nobody", None):
        findings.append(Finding(
            channel="Контент", severity="warning",
            fact="Контент не создаётся. Без регулярного контента все каналы теряют органический охват.",
            recommendation="Запустить минимальный контент-план: 3 поста в неделю в VK/Telegram.",
            kpi="ER > 3% через 60 дней",
            priority="high", effort="strategic",
        ))

    # Позитивные находки
    if _has(d.ch_vk):
        findings.append(Finding(
            channel="ВКонтакте", severity="ok",
            fact="Сообщество VK присутствует — хорошая база для анализа и роста.",
            recommendation="Провести аудит частоты и вовлечённости, оптимизировать контент-план.",
            kpi="ER > 4% (benchmark для ниши)",
            priority="medium", effort="strategic",
        ))

    if _has(d.website):
        findings.append(Finding(
            channel="Сайт", severity="ok",
            fact="Сайт присутствует — базовая точка конверсии есть.",
            recommendation="Провести технический аудит скорости и SEO, оптимизировать форму заявки.",
            kpi="Конверсия сайта +30% за 60 дней",
            priority="high", effort="strategic",
        ))

    return findings


# ─── Конкуренты ─────────────────────────────────────────────

def get_competitors(d: IntakeForm) -> List[Dict]:
    rows = []
    for i, (name, site, vk, tg, comment) in enumerate([
        (d.c1_name, d.c1_site, d.c1_vk, d.c1_tg, d.c1_comment),
        (d.c2_name, d.c2_site, getattr(d, 'c2_vk', None), getattr(d, 'c2_tg', None), None),
        (d.c3_name, d.c3_site, getattr(d, 'c3_vk', None), getattr(d, 'c3_tg', None), None),
        (d.c4_name, d.c4_site, None, None, None),
        (d.c5_name, d.c5_site, None, None, None),
    ], 1):
        if _has(name):
            rows.append({
                "num":     i,
                "name":    name,
                "site":    "✓" if _has(site) else "—",
                "vk":      "✓" if _has(vk)  else "?",
                "tg":      "✓" if _has(tg)  else "?",
                "maps":    "?",
                "comment": comment or "",
            })
    return rows


# ─── Автоматизация ──────────────────────────────────────────

def generate_automation(d: IntakeForm) -> List[Dict]:
    """Полный список вариантов автоматизации, разбитый по категориям."""

    budget_ok = d.budget not in (None, "none")
    has_dev   = d.has_dev in ("yes", "plan")
    has_crm   = _has(d.crm_name) and d.crm_name.lower() not in ("нет", "no")

    all_opts = [
        # ── CRM и воронка ─────────────────────────────────────
        {
            "cat": "CRM и воронка продаж", "cat_icon": "🔄",
            "name": "Автоквалификация входящих лидов",
            "desc": "Лид попадает в CRM → автоматически ставится задача менеджеру → через 5 минут уходит первое сообщение. Ни одна заявка не теряется.",
            "tool": "AmoCRM / Bitrix24 Rules",
            "hours": 2, "roi": 8, "priority": "high", "type": "quick_win",
        },
        {
            "cat": "CRM и воронка продаж", "cat_icon": "🔄",
            "name": "Цепочка касаний после заявки",
            "desc": "Автоматическая серия сообщений: WhatsApp → email → звонок. Настраивается один раз, работает 24/7.",
            "tool": "AmoCRM + Wazzup / WABA",
            "hours": 8, "roi": 12, "priority": "high", "type": "strategic",
        },
        {
            "cat": "CRM и воронка продаж", "cat_icon": "🔄",
            "name": "Обогащение контактов через Dadata",
            "desc": "При вводе ИНН или телефона — автозаполнение компании, адреса, реквизитов. Экономит 3 минуты на каждом лиде.",
            "tool": "Dadata API",
            "hours": 1, "roi": 4, "priority": "medium", "type": "quick_win",
        },
        {
            "cat": "CRM и воронка продаж", "cat_icon": "🔄",
            "name": "Еженедельный отчёт по воронке в Telegram",
            "desc": "Каждый понедельник в 9:00 руководитель получает автоматический отчёт: заявки, конверсия, выручка, узкие места.",
            "tool": "Bitrix24 / AmoCRM + Telegram Bot API",
            "hours": 3, "roi": 5, "priority": "high", "type": "quick_win",
        },
        {
            "cat": "CRM и воронка продаж", "cat_icon": "🔄",
            "name": "Автоматический расчёт LTV и сегментация клиентов",
            "desc": "Система автоматически делит клиентов на сегменты A/B/C по выручке и частоте — даёт понять, на кого тратить ресурсы.",
            "tool": "Bitrix24 CRM Analytics / Retable",
            "hours": 6, "roi": 9, "priority": "medium", "type": "strategic",
        },

        # ── Маркетинг ─────────────────────────────────────────
        {
            "cat": "Маркетинг и реклама", "cat_icon": "📢",
            "name": "Автопостинг по расписанию в VK и Telegram",
            "desc": "Создаёте контент один раз в неделю — система публикует сама в нужное время, в нужные каналы, с нужными хэштегами.",
            "tool": "SMMplanner / Postmypost",
            "hours": 2, "roi": 4, "priority": "high", "type": "quick_win",
        },
        {
            "cat": "Маркетинг и реклама", "cat_icon": "📢",
            "name": "Ретаргетинг на базу CRM в VK и Яндексе",
            "desc": "Загружаете телефоны клиентов → система показывает им рекламу up-sell/cross-sell. Конверсия в 4–8 раз выше холодной рекламы.",
            "tool": "VK Реклама + Яндекс.Аудитории",
            "hours": 4, "roi": 14, "priority": "high", "type": "strategic",
        },
        {
            "cat": "Маркетинг и реклама", "cat_icon": "📢",
            "name": "Look-alike аудитории на основе лучших клиентов",
            "desc": "Алгоритм VK/Яндекса находит людей, похожих на ваших топ-клиентов — CPL снижается на 30–50%.",
            "tool": "VK Реклама Lal / Яндекс.Аудитории",
            "hours": 3, "roi": 10, "priority": "high", "type": "strategic",
        },
        {
            "cat": "Маркетинг и реклама", "cat_icon": "📢",
            "name": "Автоматические ставки в Яндекс.Директ",
            "desc": "Переключение на стратегию «Оптимизация конверсий» — алгоритм сам распределяет бюджет на аудиторию с наибольшей вероятностью покупки.",
            "tool": "Яндекс.Директ Smart Bidding",
            "hours": 1, "roi": 7, "priority": "medium", "type": "quick_win",
        },
        {
            "cat": "Маркетинг и реклама", "cat_icon": "📢",
            "name": "Автоматический мониторинг репутации бренда",
            "desc": "Система оповещает в Telegram при каждом упоминании компании в сети: отзывы, соцсети, форумы. Реагируете первыми.",
            "tool": "YouScan / Google Alerts + Telegram",
            "hours": 1, "roi": 5, "priority": "medium", "type": "quick_win",
        },

        # ── Контент ───────────────────────────────────────────
        {
            "cat": "Контент и коммуникации", "cat_icon": "✍️",
            "name": "AI-генерация черновиков постов",
            "desc": "Задаёте тему → AI пишет 5 вариантов поста для VK, Telegram и Instagram. Редактор выбирает и дополняет. Экономит 2–3 часа в неделю.",
            "tool": "Claude API / ChatGPT API",
            "hours": 8, "roi": 7, "priority": "high", "type": "strategic",
        },
        {
            "cat": "Контент и коммуникации", "cat_icon": "✍️",
            "name": "Telegram-бот для квалификации и FAQ",
            "desc": "Бот встречает посетителей, отвечает на типовые вопросы, квалифицирует лид и отправляет заявку в CRM без участия менеджера.",
            "tool": "Botfather + Make.com / n8n",
            "hours": 12, "roi": 9, "priority": "high", "type": "strategic",
        },
        {
            "cat": "Контент и коммуникации", "cat_icon": "✍️",
            "name": "Автоматические ответы на типовые вопросы в VK",
            "desc": "Сообщения вида «Сколько стоит?», «Как записаться?» получают мгновенный автоответ. Скорость ответа — главный фактор конверсии.",
            "tool": "VK Сенлер / SENLER",
            "hours": 2, "roi": 5, "priority": "high", "type": "quick_win",
        },
        {
            "cat": "Контент и коммуникации", "cat_icon": "✍️",
            "name": "Кросспостинг между площадками",
            "desc": "Пост создаётся один раз → автоматически адаптируется и публикуется во всех каналах (VK, Telegram, ВКонтакте Stories) с нужным форматом.",
            "tool": "Make.com / Zapier",
            "hours": 4, "roi": 4, "priority": "medium", "type": "quick_win",
        },
        {
            "cat": "Контент и коммуникации", "cat_icon": "✍️",
            "name": "Автосбор и публикация отзывов",
            "desc": "После сделки клиент автоматически получает запрос на отзыв. Положительные отзывы публикуются в соцсетях, негативные — идут напрямую менеджеру.",
            "tool": "Usedesk / Carrot Quest",
            "hours": 5, "roi": 8, "priority": "medium", "type": "strategic",
        },

        # ── Аналитика ─────────────────────────────────────────
        {
            "cat": "Аналитика и мониторинг", "cat_icon": "📊",
            "name": "Единый дашборд всех каналов в реальном времени",
            "desc": "Один экран: заявки из CRM, трафик с сайта, охваты соцсетей, рейтинг на картах. Принимаете решения на основе данных, а не ощущений.",
            "tool": "Яндекс DataLens / Looker Studio",
            "hours": 16, "roi": 6, "priority": "high", "type": "strategic",
        },
        {
            "cat": "Аналитика и мониторинг", "cat_icon": "📊",
            "name": "Алерты при аномалиях метрик",
            "desc": "Упал трафик на 30%? Резко выросли отказы? Система мгновенно присылает уведомление в Telegram — реагируете за минуты, а не дни.",
            "tool": "Яндекс.Метрика Alerts + Telegram API",
            "hours": 2, "roi": 5, "priority": "high", "type": "quick_win",
        },
        {
            "cat": "Аналитика и мониторинг", "cat_icon": "📊",
            "name": "Сквозная аналитика: от клика до выручки",
            "desc": "Связываете рекламный кабинет → CRM → оплату. Видите точный ROI каждого канала. Перераспределяете бюджет туда, где он работает.",
            "tool": "Calltouch / Roistat / CoMagic",
            "hours": 24, "roi": 15, "priority": "high", "type": "longterm",
        },
        {
            "cat": "Аналитика и мониторинг", "cat_icon": "📊",
            "name": "Когортный анализ удержания клиентов",
            "desc": "Система автоматически строит когорты: какой % клиентов вернулся через 30/60/90 дней. Находите лучшие и худшие когорты для оптимизации.",
            "tool": "Яндекс DataLens / Mixpanel",
            "hours": 20, "roi": 9, "priority": "medium", "type": "longterm",
        },

        # ── AI ────────────────────────────────────────────────
        {
            "cat": "AI и нейросети", "cat_icon": "🤖",
            "name": "AI-чат на сайте на базе Claude / YandexGPT",
            "desc": "Чат-бот отвечает на вопросы посетителей на основе ваших материалов (прайс, FAQ, кейсы). Конвертирует посетителей в заявки 24/7.",
            "tool": "Claude API / YandexGPT API + виджет",
            "hours": 20, "roi": 12, "priority": "high", "type": "longterm",
        },
        {
            "cat": "AI и нейросети", "cat_icon": "🤖",
            "name": "Анализ тональности отзывов",
            "desc": "AI классифицирует каждый новый отзыв: позитивный / нейтральный / негативный. Критичные отзывы — сразу в Telegram руководителю.",
            "tool": "Claude API / natasha + Python",
            "hours": 8, "roi": 6, "priority": "medium", "type": "strategic",
        },
        {
            "cat": "AI и нейросети", "cat_icon": "🤖",
            "name": "Предсказание оттока клиентов (Churn Prediction)",
            "desc": "ML-модель на основе истории CRM предсказывает, кто из клиентов уйдёт в ближайшие 30 дней. Менеджер получает список с рекомендациями по удержанию.",
            "tool": "Python sklearn + AmoCRM API",
            "hours": 40, "roi": 18, "priority": "medium", "type": "longterm",
        },
        {
            "cat": "AI и нейросети", "cat_icon": "🤖",
            "name": "AI-помощник для менеджеров продаж",
            "desc": "Перед каждым звонком менеджер получает AI-сводку: история клиента, лучший скрипт, вероятность сделки, рекомендуемый оффер.",
            "tool": "Claude API + AmoCRM Widget",
            "hours": 24, "roi": 11, "priority": "medium", "type": "longterm",
        },
        {
            "cat": "AI и нейросети", "cat_icon": "🤖",
            "name": "Автоматическая сегментация базы контактов",
            "desc": "Алгоритм кластеризации делит всю базу на сегменты по поведению, выручке, частоте покупок — без ручной разметки.",
            "tool": "Python + CRM API",
            "hours": 16, "roi": 8, "priority": "medium", "type": "strategic",
        },

        # ── Операции ──────────────────────────────────────────
        {
            "cat": "Операционная эффективность", "cat_icon": "⚙️",
            "name": "Интеграция всех сервисов через Make.com / n8n",
            "desc": "Один хаб автоматизации объединяет CRM, мессенджеры, Google Sheets, аналитику. Данные текут между системами без ручного переноса.",
            "tool": "Make.com (Integromat) / n8n self-hosted",
            "hours": 12, "roi": 7, "priority": "high", "type": "strategic",
        },
        {
            "cat": "Операционная эффективность", "cat_icon": "⚙️",
            "name": "Автоматизация документооборота (КП, договоры)",
            "desc": "Менеджер нажимает кнопку в CRM → система автоматически генерирует КП / договор с данными клиента и отправляет на подпись.",
            "tool": "Bitrix24 + DocuSign / Контур.Подпись",
            "hours": 8, "roi": 5, "priority": "medium", "type": "strategic",
        },
        {
            "cat": "Операционная эффективность", "cat_icon": "⚙️",
            "name": "Автосинхронизация цен и остатков",
            "desc": "Цены из 1С / Google Sheets автоматически обновляются на сайте, Avito, маркетплейсах. Исключает несоответствие цен и ручной труд.",
            "tool": "1С + API сайта / YML-фид",
            "hours": 6, "roi": 5, "priority": "medium", "type": "quick_win",
        },
    ]

    # Группировка по категориям
    from collections import defaultdict
    grouped: Dict[str, List] = defaultdict(list)
    for opt in all_opts:
        grouped[opt["cat"]].append(opt)

    result = []
    for cat, opts in grouped.items():
        result.append({
            "cat":  cat,
            "icon": opts[0]["cat_icon"],
            "opts": opts,
        })
    return result


# ─── Дорожная карта ─────────────────────────────────────────

def generate_roadmap(findings: List[Finding]) -> List[Dict]:
    quick_wins  = [f for f in findings if f.effort == "quick_win"  and f.severity in ("critical","warning")]
    strategic   = [f for f in findings if f.effort == "strategic"]
    longterm    = [f for f in findings if f.effort == "longterm"]

    return [
        {
            "phase": "Фаза 1",
            "period": "Месяц 1",
            "title": "Быстрые победы",
            "color": "#10b981",
            "items": [
                "Заполнить карточку Яндекс.Карты / 2ГИС",
                "Подключить Яндекс.Метрику с целями",
                "Настроить автоответы в VK / Telegram",
                "Базовый SEO-аудит сайта и исправление критичных ошибок",
                "Настроить CRM и автоквалификацию лидов",
                "Запустить алерты при аномалиях трафика",
            ],
            "result": "Закрыты все критичные пробелы. Лиды перестают теряться.",
        },
        {
            "phase": "Фаза 2",
            "period": "Месяцы 2–3",
            "title": "Рост и системность",
            "color": "#2563eb",
            "items": [
                "Запустить VK-сообщество / Telegram-канал с контент-планом",
                "Настроить автопостинг через SMMplanner",
                "Запустить ретаргетинг на базу CRM",
                "Создать Telegram-бот для квалификации лидов",
                "Внедрить единый дашборд метрик",
                "Запустить AI-генерацию черновиков контента",
            ],
            "result": "+30–50% входящих заявок. Все процессы работают без ручного контроля.",
        },
        {
            "phase": "Фаза 3",
            "period": "Месяцы 4–6",
            "title": "Масштабирование",
            "color": "#7c3aed",
            "items": [
                "Развернуть AI-чат на сайте (Claude / YandexGPT)",
                "Настроить сквозную аналитику до рубля",
                "Запустить Look-alike аудитории",
                "Внедрить когортный анализ и Churn Prediction",
                "Автоматизировать документооборот",
                "Провести повторный стратегический аудит",
            ],
            "result": "Полная воронка автоматизирована. Рост LTV клиентов на 20–40%.",
        },
    ]


# ─── Сборка отчёта ──────────────────────────────────────────

def generate_report(data: dict, project_id: str) -> str:
    d = IntakeForm(**data)

    channels    = analyze_channels(d)
    findings    = generate_findings(d)
    competitors = get_competitors(d)
    automation  = generate_automation(d)
    roadmap     = generate_roadmap(findings)

    goals_human     = [GOAL_LABELS.get(g, g) for g in (d.goal or [])]
    discovery_human = [DISCOVERY_LABELS.get(g, g) for g in (d.discovery or [])]
    budget_human    = BUDGET_LABELS.get(d.budget, "Не указан")
    content_human   = CONTENT_LABELS.get(d.content_creator, "Не указано")

    comps_list = [n for n in [d.c1_name, d.c2_name, d.c3_name, d.c4_name, d.c5_name] if _has(n)]

    # Radar chart data: channel scores
    ch_scores = [c["score"] for c in channels]

    ctx = dict(
        project_id      = project_id,
        generated_at    = datetime.now().strftime("%d.%m.%Y"),
        company_name    = d.company_name,
        website         = d.website or "—",
        location        = d.location or "—",
        niche           = d.niche or "—",
        product         = d.product or "—",
        segments        = d.segments or "—",
        budget          = budget_human,
        content_creator = content_human,
        goals           = goals_human,
        goal_result     = d.goal_result or "",
        discovery       = discovery_human,
        typical_client  = d.typical_client or "",
        deadline        = d.deadline or "Не указан",
        what_works      = d.what_works or "",
        what_failed     = d.what_failed or "",
        differentiator  = d.differentiator or "",
        strongest       = d.strongest or "",
        # Метрики
        m1_cur=d.m1_cur or "—", m1_want=d.m1_want or "—",
        m2_cur=d.m2_cur or "—", m2_want=d.m2_want or "—",
        m3_cur=d.m3_cur or "—", m3_want=d.m3_want or "—",
        m4_cur=d.m4_cur or "—", m4_want=d.m4_want or "—",
        m5_cur=d.m5_cur or "—", m5_want=d.m5_want or "—",
        # Аналитика
        acc_metrika = ACCESS_LABELS.get(d.acc_metrika, ("—", "none")),
        acc_ga      = ACCESS_LABELS.get(d.acc_ga, ("—", "none")),
        crm_name    = d.crm_name or "—",
        monthly_leads = d.monthly_leads or "—",
        close_rate    = d.close_rate or "—",
        # Данные для шаблона
        channels    = channels,
        findings    = findings,
        competitors = competitors,
        automation  = automation,
        roadmap     = roadmap,
        ch_scores   = ch_scores,
        comps_count = len(comps_list),
        findings_critical = len([f for f in findings if f.severity == "critical"]),
        findings_opportunity = len([f for f in findings if f.severity == "opportunity"]),
        total_auto_options = sum(len(cat["opts"]) for cat in automation),
    )

    tpl = env.get_template("report.html")
    return tpl.render(**ctx)
