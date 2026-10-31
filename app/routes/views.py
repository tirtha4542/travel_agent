from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

router = APIRouter(tags=["views"])


@router.get("/", response_class=HTMLResponse)
async def index_page(request: Request):
    """Renders the main TreapMate AI single-page chat workspace."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request, "title": "TreapMate AI - Autonomous Travel Agent"}
    )
