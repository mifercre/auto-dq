from typing import Generator
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN

from core.config import settings
from db.session import SessionLocal


# API key authentication to be used for server-to-server workflows such as updating DQ table partition metadata
# directly from a Hive ETL script
api_key_header = APIKeyHeader(name=settings.API_KEY_NAME, auto_error=False)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == settings.API_KEY:
        return api_key_header
    else:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail='Could not validate credentials')
