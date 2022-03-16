from urllib.parse import unquote

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi_sqlalchemy import DBSessionMiddleware, db
from fastapi.templating import Jinja2Templates
from pydantic.types import Json

from .db import Credentials
from .settings import Settings

app = FastAPI()
settings = Settings()
templates = Jinja2Templates(directory="templates")
app.add_middleware(DBSessionMiddleware, db_url=settings.DB_DSN)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "groups": settings.GROUPS,
            "google_creds": settings.GOOGLE_CREDS
        },
    )


@app.get("/credentials")
def get_credentials(
    code: str,
    scope: str,
    state: Json,
    prompt: str,
    authuser: int = 0,
    hd: str = "gmail.com",
):
    scope = scope.split(unquote("%20"))
    group = state.get("group")

    if not group:
        raise HTTPException(403, "No group provided")

    db.session.add(
        Credentials(
            code=code,
            scope=scope,
            group=group,
            prompt=prompt,
            authuser=authuser,
            hd=hd,
        )
    )
    db.session.commit()

    return RedirectResponse(settings.REDIRECT_URL)
