"""
Модели данных Стратег v2
Основаны на brief.md: SourceResult, Finding, ProjectResearch
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime


class IntakeForm(BaseModel):
    """Данные анкеты от представителя компании."""
    # Раздел 1
    company_name: str
    legal_name: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    niche: Optional[str] = None
    product: Optional[str] = None
    segments: Optional[str] = None
    # Раздел 2 — каналы
    ch_site: Optional[str] = None
    ch_landings: Optional[str] = None
    ch_vk: Optional[str] = None
    ch_tg_channel: Optional[str] = None
    ch_tg_bot: Optional[str] = None
    ch_instagram: Optional[str] = None
    ch_youtube: Optional[str] = None
    ch_ymaps: Optional[str] = None
    ch_2gis: Optional[str] = None
    ch_avito: Optional[str] = None
    ch_wa: Optional[str] = None
    ch_other: Optional[str] = None
    # Раздел 3 — цели
    goal: Optional[List[str]] = []
    goal_result: Optional[str] = None
    # Раздел 4 — метрики
    m1_cur: Optional[str] = None
    m1_want: Optional[str] = None
    m2_cur: Optional[str] = None
    m2_want: Optional[str] = None
    m3_cur: Optional[str] = None
    m3_want: Optional[str] = None
    m4_cur: Optional[str] = None
    m4_want: Optional[str] = None
    m5_cur: Optional[str] = None
    m5_want: Optional[str] = None
    # Раздел 5 — ресурсы
    budget: Optional[str] = None
    content_creator: Optional[str] = None
    hours_week: Optional[str] = None
    has_dev: Optional[str] = None
    # Раздел 6 — доступ
    acc_metrika: Optional[str] = None
    acc_ga: Optional[str] = None
    analytics_detail: Optional[List[str]] = []
    crm_name: Optional[str] = None
    crm_access: Optional[str] = None
    monthly_leads: Optional[int] = None
    close_rate: Optional[int] = None
    acc_vk_ads: Optional[str] = None
    acc_direct: Optional[str] = None
    # Раздел 7 — конкуренты
    c1_name: Optional[str] = None
    c1_site: Optional[str] = None
    c1_vk: Optional[str] = None
    c1_tg: Optional[str] = None
    c1_comment: Optional[str] = None
    c2_name: Optional[str] = None
    c2_site: Optional[str] = None
    c3_name: Optional[str] = None
    c3_site: Optional[str] = None
    c4_name: Optional[str] = None
    c4_site: Optional[str] = None
    c4_comment: Optional[str] = None
    c5_name: Optional[str] = None
    c5_site: Optional[str] = None
    c5_comment: Optional[str] = None
    strongest: Optional[str] = None
    differentiator: Optional[str] = None
    # Раздел 8 — ситуация
    what_failed: Optional[str] = None
    what_works: Optional[str] = None
    prev_audit: Optional[str] = None
    audit_result: Optional[str] = None
    seasonality: Optional[str] = None
    season_peak: Optional[str] = None
    season_low: Optional[str] = None
    # Раздел 9 — аудитория
    typical_client: Optional[str] = None
    best_segments: Optional[str] = None
    target_segments: Optional[str] = None
    discovery: Optional[List[str]] = []
    # Раздел 10
    future_plans: Optional[str] = None
    constraints: Optional[str] = None
    deadline: Optional[str] = None


class Finding(BaseModel):
    channel: str
    severity: Literal['critical', 'warning', 'opportunity', 'ok']
    fact: str
    recommendation: Optional[str] = None
    kpi: Optional[str] = None
    priority: Literal['high', 'medium', 'low']
    effort: Literal['quick_win', 'strategic', 'longterm']


class AutomationOption(BaseModel):
    category: str
    name: str
    description: str
    tool: str
    effort_hours: int
    roi_x: int
    priority: Literal['high', 'medium', 'low']
    type: Literal['quick_win', 'strategic', 'longterm']


class ReportResponse(BaseModel):
    project_id: str
    report_url: str
    company_name: str
    created_at: str
