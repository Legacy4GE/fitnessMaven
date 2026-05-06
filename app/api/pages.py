from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/test", response_class=HTMLResponse)
def test_page():
    with open("static/test.html") as f:
        return f.read()
