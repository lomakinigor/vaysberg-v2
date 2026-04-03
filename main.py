"""
Стратег API — FastAPI backend
Запуск: uvicorn main:app --reload --port 8000
"""
import uuid
import json
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from report_generator import generate_report

load_dotenv()

app = FastAPI(title="Стратег API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)

# Статика — отдаём index.html и всё из корня
app.mount("/static", StaticFiles(directory="."), name="static")


@app.get("/", response_class=FileResponse)
async def root():
    return FileResponse("index.html")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "Стратег API"}


@app.post("/api/intake")
async def submit_intake(request: Request):
    """
    Принимает данные анкеты → генерирует отчёт → возвращает URL.
    """
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"error": "Неверный формат данных"}, status_code=400)

    company = data.get("company_name", "company")
    project_id = f"{datetime.now().strftime('%Y%m%d')}_{str(uuid.uuid4())[:6]}"

    # Сохраняем анкету
    intake_path = REPORTS_DIR / f"{project_id}_intake.json"
    intake_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Генерируем HTML-отчёт
    try:
        report_html = generate_report(data, project_id)
    except Exception as e:
        return JSONResponse({"error": f"Ошибка генерации отчёта: {e}"}, status_code=500)

    report_path = REPORTS_DIR / f"{project_id}_report.html"
    report_path.write_text(report_html, encoding="utf-8")

    return {
        "project_id": project_id,
        "report_url": f"/report/{project_id}",
        "company_name": company,
        "created_at": datetime.now().isoformat(),
    }


@app.get("/report/{project_id}", response_class=HTMLResponse)
async def get_report(project_id: str):
    report_path = REPORTS_DIR / f"{project_id}_report.html"
    if not report_path.exists():
        return HTMLResponse(
            "<h2>Отчёт не найден</h2><p>Проверьте правильность ссылки.</p>",
            status_code=404,
        )
    return HTMLResponse(report_path.read_text(encoding="utf-8"))


@app.get("/reports")
async def list_reports():
    """Список всех сгенерированных отчётов."""
    items = []
    for f in sorted(REPORTS_DIR.glob("*_intake.json"), reverse=True):
        pid = f.stem.replace("_intake", "")
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            items.append({
                "project_id":   pid,
                "company_name": data.get("company_name", "—"),
                "report_url":   f"/report/{pid}",
                "created_at":   f.stat().st_mtime,
            })
        except Exception:
            pass
    return items
