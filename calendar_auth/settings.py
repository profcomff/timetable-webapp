from pydantic import BaseSettings, Json, PostgresDsn, AnyHttpUrl
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings"""

    DB_DSN: PostgresDsn
    PATH_TO_GOOGLE_CREDS: str
    APP_URL: Optional[AnyHttpUrl] = None
    REDIRECT_URL: AnyHttpUrl = "https://www.profcomff.com"
    GROUPS: List[str] = ["101", "102"]
    DEFAULT_GROUP = '{group: 0}'
    SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/userinfo.email']

    class Config:
        """Pydantic BaseSettings config"""

        case_sensitive = True
        env_file = ".env"
