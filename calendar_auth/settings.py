from pydantic import BaseSettings, Json, PostgresDsn, AnyHttpUrl
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    DB_DSN: PostgresDsn
    GOOGLE_CREDS: Json
    REDIRECT_URL: AnyHttpUrl = "https://www.profcomff.com"
    GROUPS: List[str] = ["101", "102"]

    class Config:
        """Pydantic BaseSettings config"""

        case_sensitive = True
        env_file = ".env"
