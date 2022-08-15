from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn, validator


class Settings(BaseSettings):
    API_PREFIX_ADMIN: str = '/admin'
    API_PREFIX_EXTERNAL: str = '/api'
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30
    SERVER_NAME: str
    SERVER_HOST: AnyHttpUrl
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        'http://localhost:3000', 'http://localhost:8001',
    ]

    @validator('BACKEND_CORS_ORIGINS', pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith('['):
            return [i.strip() for i in v.split(',')]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str

    # Backend metadata DB configs
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator('SQLALCHEMY_DATABASE_URI', pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme='postgresql',
            user=values.get('POSTGRES_USER'),
            password=values.get('POSTGRES_PASSWORD'),
            host=values.get('POSTGRES_SERVER'),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    REDIS_BACKEND: str = 'redis://redis:6379/0'

    # Mattermost hook to send alerts to
    MATTERMOST_HOOK: str

    # External API token
    API_KEY_NAME: str = 'access-token'
    API_KEY: str

    class Config:
        case_sensitive = True
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
