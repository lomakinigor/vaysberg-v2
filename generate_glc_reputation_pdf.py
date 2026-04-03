#!/usr/bin/env python3
"""
Стратегический анализ ГПК «Репутация» → PDF
Имя файла: Стратегический_анализ_ГПК_Репутация_2026-04-02.pdf
"""

from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# --- Регистрируем шрифты с кириллицей ---
FONTS_DIR = Path("/usr/share/fonts/truetype/dejavu")
pdfmetrics.registerFont(TTFont("DejaVu", str(FONTS_DIR / "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", str(FONTS_DIR / "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DejaVu-Mono", str(FONTS_DIR / "DejaVuSansMono.ttf")))

# --- Цветовая палитра ---
C_DARK   = colors.HexColor("#1a2e4a")
C_BLUE   = colors.HexColor("#1e5799")
C_LIGHT  = colors.HexColor("#3a80c8")
C_ACCENT = colors.HexColor("#e05c1a")
C_RED    = colors.HexColor("#c0392b")
C_YELLOW = colors.HexColor("#f39c12")
C_GREEN  = colors.HexColor("#27ae60")
C_GRAY   = colors.HexColor("#7f8c8d")
C_BG     = colors.HexColor("#f4f7fb")
C_WHITE  = colors.white
C_ROW1   = colors.HexColor("#eaf1fb")
C_ROW2   = colors.white

PAGE_W, PAGE_H = A4
M = 18 * mm  # поля


def make_styles():
    base = getSampleStyleSheet()

    def s(name, parent="Normal", **kw):
        defaults = dict(fontName="DejaVu", fontSize=10, leading=14,
                        textColor=C_DARK, spaceAfter=4)
        defaults.update(kw)
        return ParagraphStyle(name, parent=base[parent], **defaults)

    return {
        "title":    s("title",    fontSize=22, fontName="DejaVu-Bold",
                      textColor=C_WHITE, alignment=TA_CENTER, spaceAfter=2, leading=28),
        "subtitle": s("subtitle", fontSize=11, textColor=colors.HexColor("#c8ddf7"),
                      alignment=TA_CENTER, spaceAfter=0),
        "meta":     s("meta",     fontSize=9,  textColor=colors.HexColor("#b0c8e8"),
                      alignment=TA_CENTER, spaceAfter=0),
        "h1":       s("h1",       fontSize=15, fontName="DejaVu-Bold",
                      textColor=C_WHITE, spaceBefore=0, spaceAfter=0,
                      alignment=TA_LEFT, leading=20),
        "h2":       s("h2",       fontSize=12, fontName="DejaVu-Bold",
                      textColor=C_BLUE,  spaceBefore=8, spaceAfter=4, leading=16),
        "h3":       s("h3",       fontSize=10, fontName="DejaVu-Bold",
                      textColor=C_DARK,  spaceBefore=6, spaceAfter=3, leading=14),
        "body":     s("body",     fontSize=9.5, leading=14, alignment=TA_JUSTIFY,
                      spaceAfter=4),
        "bullet":   s("bullet",   fontSize=9.5, leading=13, leftIndent=12,
                      firstLineIndent=0, spaceAfter=2),
        "note":     s("note",     fontSize=8.5, textColor=C_GRAY, leading=12,
                      spaceAfter=4),
        "kpi":      s("kpi",      fontSize=9, fontName="DejaVu-Bold",
                      textColor=C_BLUE, spaceAfter=2),
        "warning":  s("warning",  fontSize=9, textColor=C_RED, leading=13),
        "footer":   s("footer",   fontSize=7.5, textColor=C_GRAY, alignment=TA_CENTER),
        "th":       s("th",       fontSize=8.5, fontName="DejaVu-Bold",
                      textColor=C_WHITE, alignment=TA_CENTER, leading=11),
        "td":       s("td",       fontSize=8.5, leading=12),
        "tdc":      s("tdc",      fontSize=8.5, leading=12, alignment=TA_CENTER),
    }


ST = make_styles()


# ─── Вспомогательные строительные блоки ──────────────────────────────────────

def section_header(text):
    """Синяя плашка-заголовок раздела."""
    tbl = Table([[Paragraph(text, ST["h1"])]], colWidths=[PAGE_W - 2 * M])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_BLUE),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("ROUNDEDCORNERS", [4]),
    ]))
    return tbl


def hr():
    return HRFlowable(width="100%", thickness=0.5, color=C_LIGHT,
                      spaceAfter=4, spaceBefore=4)


def sp(h=4):
    return Spacer(1, h * mm)


def h2(text):
    return Paragraph(text, ST["h2"])


def h3(text):
    return Paragraph(text, ST["h3"])


def body(text):
    return Paragraph(text, ST["body"])


def bullet(text, icon="•"):
    return Paragraph(f"{icon} {text}", ST["bullet"])


def note(text):
    return Paragraph(f"<i>{text}</i>", ST["note"])


def kpi_line(text):
    return Paragraph(f"📊 {text}", ST["kpi"])


def simple_table(data, col_widths, header_bg=C_BLUE, zebra=True):
    """Таблица с заголовком и зеброй."""
    rows = []
    for i, row in enumerate(data):
        cells = []
        for cell in row:
            if isinstance(cell, str):
                style = ST["th"] if i == 0 else ST["td"]
                cells.append(Paragraph(cell, style))
            else:
                cells.append(cell)
        rows.append(cells)

    t = Table(rows, colWidths=col_widths, repeatRows=1)
    cmds = [
        ("BACKGROUND",    (0, 0), (-1, 0),  header_bg),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  C_WHITE),
        ("FONTNAME",      (0, 0), (-1, 0),  "DejaVu-Bold"),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#c0cfe0")),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]
    if zebra:
        for r in range(1, len(data)):
            bg = C_ROW1 if r % 2 == 1 else C_ROW2
            cmds.append(("BACKGROUND", (0, r), (-1, r), bg))
    t.setStyle(TableStyle(cmds))
    return t


def priority_badge(level: str):
    """Цветной бейдж приоритета."""
    mapping = {
        "🔴 Критично":  C_RED,
        "🔴 Высокий":   C_RED,
        "🟡 Средний":   C_YELLOW,
        "🟢 Низкий":    C_GREEN,
    }
    color = mapping.get(level, C_GRAY)
    style = ParagraphStyle("badge", parent=ST["tdc"],
                           textColor=color, fontName="DejaVu-Bold")
    return Paragraph(level, style)


# ─── Обложка ─────────────────────────────────────────────────────────────────

def cover_page():
    elems = []

    # Тёмный баннер-заголовок
    banner_data = [[
        Paragraph("СТРАТЕГИЧЕСКИЙ АНАЛИЗ", ST["title"]),
        Paragraph("ГПК «Репутация»", ST["subtitle"]),
        Paragraph("Екатеринбург, Урал | 2 апреля 2026", ST["meta"]),
        Paragraph("Методология: research.md v2.0", ST["meta"]),
    ]]
    # Вертикальный стек через вложенную таблицу
    inner = Table(
        [[Paragraph("СТРАТЕГИЧЕСКИЙ АНАЛИЗ", ST["title"])],
         [Paragraph("ГПК «Репутация»", ST["subtitle"])],
         [sp(2)],
         [Paragraph("Екатеринбург, Урал  •  2 апреля 2026  •  Методология: research.md v2.0",
                    ST["meta"])]],
        colWidths=[PAGE_W - 2 * M - 20]
    )
    inner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_DARK),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
    ]))

    outer = Table([[inner]], colWidths=[PAGE_W - 2 * M])
    outer.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C_DARK),
        ("TOPPADDING",    (0, 0), (-1, -1), 20),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 20),
        ("LEFTPADDING",   (0, 0), (-1, -1), 18),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 18),
    ]))

    elems += [sp(20), outer, sp(10)]

    # Блок входных данных
    elems.append(h2("Входные данные"))
    elems.append(simple_table(
        [
            ["Параметр", "Значение"],
            ["Компания",     "Группа Правовых Компаний «Репутация»"],
            ["Сайт",         "glc-reputation.ru"],
            ["Регион",       "Екатеринбург, Урал, Россия"],
            ["Основной фокус", "Юридические услуги для бизнеса"],
            ["Каналы",       "Сайт, VK, Telegram (@reputation_glc), Авито, 2ГИС"],
            ["CRM",          "Битрикс24"],
            ["Бизнес-цель",  "Увеличить выручку вдвое"],
        ],
        col_widths=[60 * mm, PAGE_W - 2 * M - 60 * mm],
    ))

    elems += [sp(8)]

    # Блок Executive Summary в рамке
    summary_inner = Table([
        [h3("Executive Summary")],
        [body(
            "ГПК «Репутация» — действующая юридическая компания с 8-летней историей, "
            "CRM на Битрикс24 и присутствием на ключевых платформах. "
            "Главный барьер роста — <b>отсутствие B2B-упаковки</b>: сайт не разделяет "
            "предложения для бизнеса и физлиц, нет цен-ориентиров, нет кейсов, "
            "нет FAQ. Воронка имеет критический провал на этапе «Желание/Решение» — "
            "клиент уходит, не найдя оснований для звонка. "
            "Telegram-аудитория (132 подписчика) и VK требуют пересмотра "
            "контентной стратегии под B2B. "
            "Битрикс24 даёт платформу для автоматизации, которая пока не используется в полную силу."
        )],
        [sp(2)],
        [body(
            "<b>Путь к удвоению выручки:</b> три параллельных направления — "
            "(1) переупаковать предложение под B2B, "
            "(2) замкнуть аналитику и автоматизировать первый контакт, "
            "(3) системно наращивать доверие через отзывы и контент."
        )],
    ], colWidths=[PAGE_W - 2 * M - 20])
    summary_inner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_BG),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ("BOX", (0, 0), (-1, -1), 1, C_LIGHT),
    ]))
    summary_outer = Table([[summary_inner]], colWidths=[PAGE_W - 2 * M])
    summary_outer.setStyle(TableStyle([
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
    ]))
    elems.append(summary_outer)

    elems.append(PageBreak())
    return elems


# ─── Раздел 1: Отрасль и ЦА ─────────────────────────────────────────────────

def section_industry():
    elems = [section_header("Раздел 1. Отрасль, ниша, целевая аудитория"), sp(5)]

    elems += [
        h2("1.1 Рынок и ниша"),
        body(
            "Компания работает в сегменте юридических услуг (ОКВЭД 69.10). "
            "Рынок Екатеринбурга высококонкурентный: сотни частных юристов, "
            "адвокатских бюро и юридических компаний. Дифференциация критична. "
            "Тренд 2024–2026: рост спроса на защиту бизнеса — споры с контрагентами, "
            "налоговые проверки, субсидиарная ответственность, банкротства дебиторов."
        ),
        sp(3),
        h2("1.2 Текущая vs приоритетная целевая аудитория"),
        body(
            "<b>Критическое наблюдение:</b> набор услуг на сайте — универсальный. "
            "Семейные споры и уголовные дела ориентированы на физлиц; арбитраж и "
            "экспертиза договоров — на бизнес. При заявленной цели «юридические услуги "
            "для бизнеса» специализация на сайте этот приоритет не отражает."
        ),
        sp(3),
    ]

    elems.append(simple_table(
        [
            ["Сегмент", "Ключевые боли", "Где ищет юриста"],
            ["МСБ: ИП и ООО\n(до 50 чел.)",
             "Споры с контрагентами, взыскание долгов,\nналоговые проверки",
             "Яндекс, 2ГИС, рекомендации"],
            ["Средний бизнес\n(50–200 чел.)",
             "Арбитраж, трудовые споры,\nбанкротство дебиторов",
             "Яндекс.Директ, партнёрские связи"],
            ["Физлица с\nимущественными спорами",
             "Взыскание долгов, недвижимость,\nнаследство",
             "Авито, Яндекс, карты"],
        ],
        col_widths=[45 * mm, 70 * mm, PAGE_W - 2 * M - 115 * mm],
    ))

    elems += [
        sp(3),
        note("ЦА определена на основе анализа услуг на сайте glc-reputation.ru и описания "
             "Telegram-канала по состоянию на 02.04.2026 (источник уровня 1)."),
    ]

    elems.append(PageBreak())
    return elems


# ─── Раздел 4: Каналы ────────────────────────────────────────────────────────

def section_channels():
    elems = [section_header("Раздел 4. Анализ каналов продвижения"), sp(5)]

    # --- 4.1 Сайт ---
    elems += [h2("4.1 Сайт — glc-reputation.ru"), hr()]

    elems.append(simple_table(
        [
            ["Элемент", "Статус", "Наблюдение"],
            ["H1", "✅ Есть",
             "«Группа Правовых Компаний Репутация» — корпоративное название, не ключевой запрос"],
            ["H2", "⚠️ Слабо",
             "«Что мы представляем?», «Почему мы лучшие?» — общие, без SEO-семантики"],
            ["Цены / пакеты", "❌ Нет",
             "Критический барьер для B2B-клиента"],
            ["B2B-раздел", "❌ Нет",
             "Нет отдельной страницы под бизнес-услуги"],
            ["FAQ", "❌ Нет",
             "Возражения клиента не закрыты"],
            ["Отзывы", "⚠️ Устарели",
             "4 отзыва, последний — 2023 год; все от физлиц"],
            ["Кейсы для бизнеса", "❌ Нет",
             "Нет доказательств B2B-экспертизы"],
            ["Аналитика", "✅ Есть",
             "Яндекс.Метрика, LiveInternet"],
            ["Мобильная версия", "⚠️ Частично",
             "Элементы адаптивного дизайна присутствуют"],
            ["CMS", "⚠️",
             "Megagroup.ru — шаблонная, ограниченные SEO и кастомизация"],
            ["Email", "⚠️ Слабо",
             "pravo-3616198@yandex.ru — выглядит непрофессионально для B2B"],
        ],
        col_widths=[38 * mm, 28 * mm, PAGE_W - 2 * M - 66 * mm],
    ))

    elems += [
        sp(3),
        h3("Ключевые проблемы сайта:"),
        bullet("Нет цен → B2B клиент не может оценить бюджет без звонка → высокий барьер входа", "🔴"),
        bullet("Нет кейсов для юрлиц → нет доказательства экспертизы в корпоративных спорах", "🔴"),
        bullet("Нет FAQ → типовые возражения (дорого, долго, а вдруг проиграете) не закрыты", "🟡"),
        bullet("H1 и заголовки без SEO-запросов → низкая органическая видимость", "🟡"),
        bullet("Отзывы 2020–2023 → нет свежих социальных доказательств", "🟡"),
        sp(4),
    ]

    # --- 4.2 VK ---
    elems += [h2("4.2 ВКонтакте"), hr(),
              note("⚠️ Прямой API-доступ недоступен. Наличие страницы подтверждено ссылкой на сайте. "
                   "Для полноценного анализа необходима ручная проверка."),
              h3("Что проверить вручную:"),
              bullet("Количество подписчиков и дата последнего поста"),
              bullet("Наличие раздела «Услуги/Товары» с ценами"),
              bullet("Закреплённый пост — есть ли оффер"),
              bullet("Кнопка «Написать» / «Записаться»"),
              bullet("Частота публикаций (постов в неделю)"),
              sp(4)]

    # --- 4.3 Telegram ---
    elems += [h2("4.3 Telegram — @reputation_glc"), hr()]

    elems.append(simple_table(
        [
            ["Метрика", "Значение"],
            ["Название",          "«Репутация | Юристы, возвращающие деньги»"],
            ["Подписчики",        "132"],
            ["Позиционирование",  "«Защищаем бизнес и граждан от потерь»"],
            ["Бот для заявок",    "@One_make_bot ✅"],
            ["Ссылка на сайт",    "✅ Есть"],
            ["Частота публикаций", "Не верифицирована (закрытая история)"],
            ["Охват / ER",        "Недоступны (закрытая статистика Telegram)"],
        ],
        col_widths=[55 * mm, PAGE_W - 2 * M - 55 * mm],
    ))

    elems += [
        sp(3),
        body("<b>132 подписчика</b> — очень малая аудитория. Органический рост без "
             "системного контента займёт годы."),
        body("Позиционирование «Юристы, возвращающие деньги» — B2C-слоган. "
             "При цели «B2B-юристика» расходится со стратегией."),
        body("Бот @One_make_bot — потенциально сильный инструмент захвата заявок 24/7. "
             "Критично верифицировать: передаются ли заявки в Битрикс24."),
        note("Количественные метрики Telegram закрыты. Анализ основан на публичном "
             "превью канала (источник уровня 1 с ограничениями по метрикам)."),
        sp(4),
    ]

    # --- 4.4 Карты ---
    elems += [h2("4.4 Авито и 2ГИС"), hr(),
              note("⚠️ Прямой верификации карточек не проводилось. Данные предоставлены клиентом."),
              body("Для Екатеринбурга 2ГИС — один из основных каналов поиска юриста, "
                   "особенно для срочных запросов. Авито — значимый источник лидов "
                   "для физлиц и малого бизнеса."),
              sp(3)]

    elems.append(simple_table(
        [
            ["Параметр",                     "2ГИС", "Авито"],
            ["Рейтинг",                      "?",    "?"],
            ["Количество отзывов",           "?",    "?"],
            ["Свежие отзывы (2025–2026)",    "?",    "?"],
            ["Фото карточки",                "?",    "?"],
            ["Описание услуг с B2B-акцентом","?",    "?"],
            ["Ответы на отзывы",             "?",    "?"],
        ],
        col_widths=[90 * mm, 35 * mm, PAGE_W - 2 * M - 125 * mm],
    ))

    elems += [sp(4), note("Рейтинг ниже 4.5 ★ и/или отсутствие свежих отзывов "
                          "прямо снижают конверсию B2B-клиента.")]
    elems.append(PageBreak())
    return elems


# ─── Раздел 4.7: Воронка ─────────────────────────────────────────────────────

def section_funnel():
    elems = [section_header("Раздел 4.7. Реверс-инжиниринг воронки продаж"), sp(5),
             note("Воронка восстановлена по методу реверс-инжиниринга открытого контента "
                  "по состоянию на 02.04.2026. Реальные конверсии между этапами неизвестны "
                  "без доступа к Яндекс.Метрике."),
             sp(3)]

    elems.append(simple_table(
        [
            ["Этап", "Что есть", "Что отсутствует", "Оценка"],
            ["1. Осведомлённость\n(первое касание)",
             "2ГИС, Авито, Яндекс.Метрика на сайте",
             "Активный SEO-контент, реклама,\nB2B-контент в Telegram",
             "🔴 Слабо"],
            ["2. Интерес\n(прогрев)",
             "Telegram-канал с тематическим\nконтентом",
             "Кейсы, блог на сайте, регулярный\nконтент с B2B-фокусом",
             "🔴 Слабо"],
            ["3. Желание/Решение",
             "4 отзыва, «8 лет», рассрочка",
             "Цены-ориентиры, FAQ, кейсы\nдля юрлиц, свежие доказательства",
             "🔴 Критично"],
            ["4. Действие\n(заявка)",
             "Форма на сайте, Telegram-бот",
             "Мессенджер-кнопка на сайте,\nбыстрый путь к заявке",
             "🟡 Частично"],
            ["5. Удержание",
             "Telegram-канал",
             "Автоматический follow-up,\nсистема сбора отзывов, реактивация",
             "🔴 Отсутствует"],
        ],
        col_widths=[38 * mm, 48 * mm, 58 * mm, PAGE_W - 2 * M - 144 * mm],
    ))

    elems += [
        sp(5),
        h3("Главный провал воронки — этап 3 (Желание/Решение):"),
        body(
            "Клиент приходит на сайт, видит общие формулировки без цен и кейсов, "
            "не находит ответа на своё возражение и уходит к конкуренту. "
            "Этапы прогрева (2) и закрытия (3) фактически не выстроены."
        ),
    ]

    elems.append(PageBreak())
    return elems


# ─── Раздел 6: Стратегия ─────────────────────────────────────────────────────

def section_strategy():
    elems = [section_header("Раздел 6. Стратегия усиления по каналам"), sp(5)]

    # Принципиальное противоречие
    warn_inner = Table([
        [h3("Принципиальное противоречие, которое нужно решить первым")],
        [body(
            "Сайт, Telegram и предположительно VK позиционируют компанию для смешанной "
            "аудитории (B2C + B2B) без чёткого разделения. Цель — рост через B2B "
            "(более высокий средний чек). Без разделения каналов и предложений по сегментам "
            "привлечение B2B-клиентов будет неэффективным."
        )],
        [body("<b>Решение:</b> создать чёткое B2B-направление с отдельной упаковкой — "
              "лендинг, кейсы, цены, контент-рубрики.")],
    ], colWidths=[PAGE_W - 2 * M - 20])
    warn_inner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fff3e0")),
        ("BOX",  (0, 0), (-1, -1), 1.5, C_ACCENT),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
    ]))
    elems += [Table([[warn_inner]], colWidths=[PAGE_W - 2 * M]), sp(6)]

    # ── 6.1 Сайт
    elems += [h2("6.1 Сайт — приоритет: КРИТИЧНЫЙ"), hr(),
              body("<b>Разрыв:</b> B2B-клиент не может принять решение о контакте без "
                   "базовой информации о стоимости и подтверждения экспертизы."),
              sp(2),
              bullet("Создать лендинг «Юристы для бизнеса»: арбитраж, взыскание долгов, "
                     "экспертиза договоров, защита директора. Отдельный URL + SEO-семантика.", "🔴"),
              bullet("Добавить ориентировочные цены / пакеты («от X ₽», «абонентское "
                     "сопровождение от Y ₽/мес»). Отсутствие цен = потеря B2B-клиента.", "🔴"),
              bullet("Добавить 5–10 кейсов для бизнеса: задача → действия → результат "
                     "(взыскано X ₽, договор защищён, субсидиарка отменена). Анонимно.", "🔴"),
              bullet("FAQ с топ-10 вопросами: «Сколько длится арбитраж?», «Работаете по "
                     "Уралу?», «Что если проиграем?», «Есть ли гарантии?»", "🟡"),
              bullet("Заменить email pravo-3616198@yandex.ru на корпоративный "
                     "@glc-reputation.ru — важный сигнал серьёзности для B2B.", "🟡"),
              bullet("Настроить цели в Яндекс.Метрике (отправка формы = конверсия) + "
                     "UTM-метки на все ссылки из соцсетей.", "🔴"),
              kpi_line("KPI: рост конверсии сайта на 30–50%; рост заявок из органики по B2B-запросам."),
              sp(5)]

    # ── 6.2 2ГИС и Авито
    elems += [h2("6.2 2ГИС и Авито — приоритет: ВЫСОКИЙ (Quick Wins)"), hr(),
              body("<b>Разрыв:</b> в Екатеринбурге большинство срочных юридических запросов "
                   "идут через 2ГИС. Рейтинг ниже 4.7 ★ и устаревшие отзывы критически "
                   "снижают доверие B2B-клиента."),
              sp(2),
              bullet("Аудит карточек 2ГИС и Авито: актуальные фото офиса/команды, "
                     "описание с B2B-акцентом, корректные часы работы.", "🔴"),
              bullet("Запустить автосбор отзывов через Битрикс24: после закрытия дела → "
                     "автосообщение клиенту со ссылкой на 2ГИС. Цель: 2–3 новых отзыва в месяц.", "🔴"),
              bullet("Отвечать на все отзывы (положительные и негативные) — "
                     "потенциальные клиенты видят это.", "🟡"),
              bullet("Авито: создать объявления по B2B-услугам с ценами «от...». "
                     "Авито ранжирует объявления с ценой выше.", "🔴"),
              kpi_line("KPI: рейтинг 2ГИС ≥ 4.7 ★; +15 новых отзывов за 6 месяцев; рост заявок с Авито."),
              sp(5)]

    # ── 6.3 Telegram
    elems += [h2("6.3 Telegram — приоритет: ВЫСОКИЙ"), hr(),
              body("<b>Разрыв:</b> 132 подписчика — канал не работает как инструмент "
                   "прогрева B2B-клиентов. Позиционирование «для всех» не привлекает бизнес."),
              sp(2),
              bullet("Сменить позиционирование на B2B: «Юридическая защита бизнеса» "
                     "в описании канала.", "🟡"),
              bullet("Ввести 3 постоянные рубрики: «Кейс недели» (реальная история + итог), "
                     "«Разбор договора» (типичные ошибки), "
                     "«Как защититься от...» (налоговая, субсидиарка, недобросовестный партнёр).", "🟡"),
              bullet("Частота: минимум 3 поста в неделю. Каждый пост — один CTA: "
                     "«Похожая ситуация? → @One_make_bot».", "🟡"),
              bullet("Верифицировать интеграцию: @One_make_bot → Битрикс24. "
                     "Заявка из бота должна автоматически создавать сделку в CRM.", "🔴"),
              bullet("Кросс-промо: ссылка на Telegram на сайте, в VK, в профилях 2ГИС и Авито.", "🟡"),
              kpi_line("KPI: рост подписчиков 132 → 500+ за 6 месяцев; 5+ заявок через бота в месяц."),
              sp(5)]

    # ── 6.4 Битрикс24
    elems += [h2("6.4 Битрикс24 — приоритет: СТРАТЕГИЧЕСКИЙ"), hr(),
              body("Битрикс24 уже есть — это главный незадействованный рычаг. "
                   "Текущий статус использования неизвестен без аудита CRM."),
              sp(2),
              bullet("Подключить все каналы (сайт, VK, Telegram-бот, Авито, звонок) "
                     "как источники в единую воронку CRM. Ни одна заявка не теряется.", "🔴"),
              bullet("Настроить UTM-метки → Яндекс.Метрика → Битрикс24 (сквозная аналитика). "
                     "Станет видно, какие каналы реально дают клиентов.", "🔴"),
              bullet("Автоответ на новую заявку < 2 минут: первый юрист, который ответил, "
                     "чаще всего получает клиента.", "🔴"),
              bullet("Автозапрос отзыва: через 3 дня после «Выиграно» → сообщение "
                     "со ссылкой на 2ГИС.", "🟡"),
              bullet("Реактивация базы: клиенты за 2–3 года → рассылка с оффером "
                     "по актуальным B2B-услугам.", "🟢"),
              kpi_line("KPI: 100% заявок в CRM с источником; конверсия заявка→сделка измерима и растёт."),
              ]

    elems.append(PageBreak())
    return elems


# ─── Раздел 7: Автоматизация ─────────────────────────────────────────────────

def section_automation():
    elems = [section_header("Раздел 7. Автоматизация"), sp(5),
             body("Битрикс24 как платформа даёт возможность автоматизировать воронку "
                  "без пропорционального роста команды. Ниже — приоритеты."),
             sp(4)]

    elems.append(simple_table(
        [
            ["Приоритет", "Автоматизация", "Инструмент", "Эффект"],
            ["🔴 1",
             "Сбор заявок из всех каналов в одну воронку",
             "Битрикс24 webhooks",
             "Ни одна заявка не теряется"],
            ["🔴 1",
             "Автоответ на новую заявку < 2 мин",
             "Триггер Битрикс24",
             "Меньше потерь на первом контакте"],
            ["🔴 1",
             "Бот: приём заявки → Битрикс24",
             "@One_make_bot + webhook",
             "Захват лидов 24/7"],
            ["🟡 2",
             "Автозапрос отзыва после закрытия дела",
             "Триггер Битрикс24 → мессенджер",
             "Системный рост рейтинга 2ГИС"],
            ["🟡 2",
             "UTM-разметка всех каналов",
             "Шаблоны UTM + Метрика",
             "Видимость: что реально работает"],
            ["🟡 2",
             "Контент-конвейер: ИИ → черновик → публикация",
             "Claude/ChatGPT + SMMplanner",
             "Регулярность без перегрузки команды"],
            ["🟢 3",
             "Реактивация базы клиентов",
             "Рассылка из Битрикс24",
             "Повторные продажи без рекламных затрат"],
        ],
        col_widths=[18 * mm, 60 * mm, 45 * mm, PAGE_W - 2 * M - 123 * mm],
    ))

    elems.append(PageBreak())
    return elems


# ─── Раздел: Сводная карта приоритетов ───────────────────────────────────────

def section_roadmap():
    elems = [section_header("Сводная карта приоритетов"), sp(5)]

    data = [
        ["#", "Действие", "Канал", "Приоритет", "Усилие", "Ожидаемый эффект"],
        ["1", "Аудит Битрикс24 + подключить все каналы",
         "CRM", "🔴 Критично", "1–2 дня", "Устраняет потери лидов"],
        ["2", "Лендинг для B2B + кейсы + FAQ на сайте",
         "Сайт", "🔴 Высокий", "2–3 нед.", "Конверсия +30–50%"],
        ["3", "Система сбора отзывов → 2ГИС",
         "2ГИС + CRM", "🔴 Высокий", "1 день", "Рост доверия и входящих"],
        ["4", "Автоответ на заявку < 2 мин",
         "Битрикс24", "🔴 Высокий", "1 день", "Меньше потерь"],
        ["5", "Авито: B2B-объявления с ценами",
         "Авито", "🔴 Высокий", "2–3 дня", "Быстрый трафик от МСБ"],
        ["6", "UTM-разметка всех каналов",
         "Аналитика", "🟡 Средний", "1 день", "Прозрачность источников"],
        ["7", "Перезапуск Telegram под B2B",
         "Telegram", "🟡 Средний", "1–2 нед.", "Прогрев долгосрочно"],
        ["8", "VK: коммерческая витрина + контент",
         "VK", "🟡 Средний", "2–3 дня", "Доп. заявки"],
        ["9", "Корпоративный email @glc-reputation.ru",
         "Сайт", "🟢 Низкий", "1 день", "Доверие B2B"],
        ["10", "Реактивация клиентской базы CRM",
         "Битрикс24", "🟢 Низкий", "1 нед.", "Повторные продажи"],
    ]

    col_widths = [8 * mm, 60 * mm, 25 * mm, 25 * mm, 18 * mm,
                  PAGE_W - 2 * M - 136 * mm]

    rows = []
    for i, row in enumerate(data):
        if i == 0:
            rows.append([Paragraph(c, ST["th"]) for c in row])
        else:
            styled = [
                Paragraph(row[0], ST["tdc"]),
                Paragraph(row[1], ST["td"]),
                Paragraph(row[2], ST["td"]),
                priority_badge(row[3]),
                Paragraph(row[4], ST["tdc"]),
                Paragraph(row[5], ST["td"]),
            ]
            rows.append(styled)

    t = Table(rows, colWidths=col_widths, repeatRows=1)
    cmds = [
        ("BACKGROUND",    (0, 0), (-1, 0),  C_BLUE),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  C_WHITE),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
        ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#c0cfe0")),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]
    for r in range(1, len(data)):
        bg = C_ROW1 if r % 2 == 1 else C_ROW2
        cmds.append(("BACKGROUND", (0, r), (-1, r), bg))
    t.setStyle(TableStyle(cmds))
    elems.append(t)
    elems.append(PageBreak())
    return elems


# ─── Итоговый раздел ─────────────────────────────────────────────────────────

def section_conclusions():
    elems = [section_header("Итоговые выводы"), sp(5)]

    # Что хорошо
    good_data = [
        [h3("Сильные стороны (использовать как базу)")],
        [bullet("Битрикс24 — платформа для автоматизации уже есть")],
        [bullet("Telegram-бот @One_make_bot — инструмент захвата заявок 24/7 (если настроен)")],
        [bullet("8+ лет работы — репутация и клиентская база для реактивации")],
        [bullet("Присутствие на 2ГИС и Авито — ключевых локальных платформах")],
        [bullet("Рассрочка до 6 месяцев — ценное УТП для МСБ, нужно вынести в акцент")],
    ]
    good_t = Table(good_data, colWidths=[PAGE_W - 2 * M - 20])
    good_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#e8f5e9")),
        ("BOX", (0, 0), (-1, -1), 1, C_GREEN),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))

    # Что плохо
    bad_data = [
        [h3("Критические проблемы (исправить в первую очередь)")],
        [bullet("Сайт не конвертирует B2B: нет цен, кейсов, FAQ — клиент уходит", "❌")],
        [bullet("Воронка прогрева отсутствует: нет системного контента ни для одного этапа", "❌")],
        [bullet("Отзывы устарели (2020–2023): нет системы автосбора новых", "❌")],
        [bullet("Битрикс24 вероятно используется не в полную силу: каналы не замкнуты", "❌")],
        [bullet("Позиционирование смешанное: ни B2B, ни B2C не чувствуют, что «это для них»", "❌")],
    ]
    bad_t = Table(bad_data, colWidths=[PAGE_W - 2 * M - 20])
    bad_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fce4e4")),
        ("BOX", (0, 0), (-1, -1), 1, C_RED),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))

    elems += [
        Table([[good_t]], colWidths=[PAGE_W - 2 * M]), sp(5),
        Table([[bad_t]],  colWidths=[PAGE_W - 2 * M]), sp(8),
    ]

    elems += [
        h2("Три рычага для удвоения выручки"),
        simple_table(
            [
                ["Рычаг", "Суть", "Горизонт"],
                ["1. Переупаковка под B2B",
                 "Лендинг, кейсы, цены-ориентиры, FAQ — чтобы клиент не уходил с сайта",
                 "1–3 мес."],
                ["2. Автоматизация первого контакта",
                 "Битрикс24, UTM, бот → ни одна заявка не теряется, скорость ответа < 2 мин",
                 "1–2 нед."],
                ["3. Системный рост доверия",
                 "Отзывы 2ГИС, контент в Telegram, кейсы — воронка прогрева работает сама",
                 "3–6 мес."],
            ],
            col_widths=[40 * mm, 100 * mm, PAGE_W - 2 * M - 140 * mm],
        ),
        sp(8),
        note(
            "Данные собраны из публичных источников в соответствии с открытым доступом платформ "
            "на дату анализа. Персональные данные авторов отзывов не собирались и не хранятся. "
            "Выводы об эффективности каналов носят ориентировочный характер — для точных данных "
            "необходим доступ к Яндекс.Метрике и Битрикс24."
        ),
    ]
    return elems


# ─── Нумерация страниц ────────────────────────────────────────────────────────

def add_page_number(canvas_obj, doc):
    canvas_obj.saveState()
    canvas_obj.setFont("DejaVu", 7.5)
    canvas_obj.setFillColor(C_GRAY)
    page_num = canvas_obj.getPageNumber()
    text = f"ГПК «Репутация» | Стратегический анализ | стр. {page_num}"
    canvas_obj.drawCentredString(PAGE_W / 2, 10 * mm, text)
    canvas_obj.restoreState()


# ─── Сборка PDF ───────────────────────────────────────────────────────────────

def build_pdf():
    output_path = Path(__file__).parent / "Стратегический_анализ_ГПК_Репутация_2026-04-02.pdf"

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=M,
        leftMargin=M,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="Стратегический анализ ГПК «Репутация»",
        author="Методология research.md v2.0",
    )

    story = []
    story += cover_page()
    story += section_industry()
    story += section_channels()
    story += section_funnel()
    story += section_strategy()
    story += section_automation()
    story += section_roadmap()
    story += section_conclusions()

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    return output_path


if __name__ == "__main__":
    print("Генерация PDF: Стратегический анализ ГПК «Репутация»...")
    path = build_pdf()
    size_kb = path.stat().st_size / 1024
    print(f"✅ Готово: {path}")
    print(f"   Размер: {size_kb:.0f} КБ")
