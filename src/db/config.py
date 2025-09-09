# config.py
from pydantic_settings import BaseSettings 
from pydantic import Field
from utils.config import get_database_url

class Settings(BaseSettings):
    db_url: str = Field(default_factory=get_database_url)
    jwt_secret: str = "CHANGE_ME"
    jwt_algo: str = "HS256"
    token_expire_minutes: int = 60 * 24
    # token_expire_minutes: int = 1

settings = Settings()