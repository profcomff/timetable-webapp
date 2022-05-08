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
from fastapi_sqlalchemy.exceptions import SessionNotInitialisedError, MissingSessionError
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
templates = Jinja2Templates(directory="templates")
app.add_middleware(DBSessionMiddleware, db_url=settings.DB_DSN)
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
user_flow = Flow.from_client_secrets_file(
    client_secrets_file=settings.PATH_TO_GOOGLE_CREDS,
    scopes=settings.SCOPES,
    state=settings.DEFAULT_GROUP_STATE,
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
    # build service to get an email address
    service = build('oauth2', 'v2', credentials=creds)
    email = service.userinfo().get().execute()['email']
    # background_tasks.add_task(get_service, creds)
    if str(group) not in settings.GROUPS:
        raise HTTPException(403, "No group provided")

    try:
        db_records = db.session.query(Credentials).filter(Credentials.email == email)

        if not db_records.count():
            db.session.add(
                Credentials(
                    group=group,
                    email=email,
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

    except SessionNotInitialisedError:
        print("DB session not initialized")
    except MissingSessionError:
        print("Missing db session")

    return RedirectResponse(settings.REDIRECT_URL)
