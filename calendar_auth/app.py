from email import message
from urllib.parse import unquote

from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi_sqlalchemy import DBSessionMiddleware, db
from fastapi.templating import Jinja2Templates
from pydantic.types import Json

from .db import Credentials
from .settings import Settings

settings = Settings()
app = FastAPI(root_path=settings.APP_URL)
templates = Jinja2Templates(directory="templates")
app.add_middleware(DBSessionMiddleware, db_url=settings.DB_DSN)


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

    db_records = db.session.query(Credentials).filter(Credentials.authuser == authuser)
    if db_records.count() == 0:
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
    else:
        db_records.update(
                dict(code=code,
                scope=scope,
                group=group,
                prompt=prompt,
                hd=hd))
    db.session.commit()

    '''async def init_service( 
        code: str,
        scope: str,
        prompt: str,
        authuser: int,
        hd: str, 
        background_tasks: BackgroundTasks
    ):
        background_tasks.add_task(get_service, code=code,
            scope=scope,
            group=group,
            prompt=prompt,
            authuser=authuser,
            hd=hd)
        return {'message': 'ок'}'''
        
    return RedirectResponse(settings.REDIRECT_URL)



    
    