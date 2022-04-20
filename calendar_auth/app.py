import json
from email import message
from urllib.parse import unquote
import os
import datetime

from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi_sqlalchemy import DBSessionMiddleware, db
from fastapi.templating import Jinja2Templates
from google_auth_oauthlib.flow import Flow
import google.oauth2.credentials
from pydantic.types import Json

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from db import Credentials
from settings import Settings

settings = Settings()
app = FastAPI(root_path=settings.APP_URL)
templates = Jinja2Templates(directory="/Users/new/PycharmProjects/timetable-webapp/templates")
app.add_middleware(DBSessionMiddleware, db_url=settings.DB_DSN)

user_flow = Flow.from_client_secrets_file(
    client_secrets_file=settings.PATH_TO_GOOGLE_CREDS,
    scopes=settings.SCOPES,
    state=settings.DEFAULT_GROUP,
    redirect_uri='http://localhost:8000/credentials'
)


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "groups": settings.GROUPS,
        },
    )


@app.get("/flow")
def get_user_flow(state: str):
    user_flow = Flow.from_client_secrets_file(
        client_secrets_file=settings.PATH_TO_GOOGLE_CREDS,
        scopes=settings.SCOPES,
        state=state,
        redirect_uri='http://localhost:8000/credentials'
    )
    return RedirectResponse(user_flow.authorization_url()[0])


@app.get("/credentials")
def get_credentials(
        background_tasks: BackgroundTasks,
        code: str,
        scope: str,
        state: Json,
):
    scope = scope.split(unquote("%20"))
    group = state.get("group")
    user_flow.fetch_token(code=code)
    creds = user_flow.credentials
    token: Json = creds.to_json()
    json_token = json.loads(token)
    client_id: str = json_token['client_id']
    is_valid_token: bool = 'refresh_token' in json_token.keys()
    #background_tasks.add_task(get_service, creds)

    if not group:
        raise HTTPException(403, "No group provided")

    db_records = db.session.query(Credentials).filter(Credentials.client_id == client_id)

    if not db_records.count() and is_valid_token:
        db.session.add(
            Credentials(
                group=group,
                client_id=client_id,
                scope=scope,
                token=token,
            )
        )
    else:
        db_records.update(
            dict(
                group=group,
                scope=scope,
            )
        )
    db.session.commit()
    return RedirectResponse(settings.REDIRECT_URL)
