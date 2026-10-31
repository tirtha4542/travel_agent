from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
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


@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Serves the application favicon to avoid 404 in browser requests."""
    return FileResponse(STATIC_DIR / "favicon.svg", media_type="image/svg+xml")
