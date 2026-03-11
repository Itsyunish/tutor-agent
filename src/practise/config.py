import secrets
from typing import Literal

from pydantic import AnyHttpUrl, EmailStr, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings): 
    """set the config variables"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )
    
    PINECONE_API_KEY: str
    PINECONE_HOST: str
    GOOGLE_API_KEY: str
    
    # REDIS_SERVER_DEV: str
    REDIS_SERVER: str
    
        
settings = Settings() 
