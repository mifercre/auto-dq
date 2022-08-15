from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import crud
import schemas
from api.deps import get_db
from core.config import settings
from db.base_class import Base
from db.session import SessionLocal
from main import app

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope='session')
def db() -> Generator:
    print('DB() BEFORE')
    yield SessionLocal()
    print('DB() AFTER')
    db = TestingSessionLocal()
    db.execute('TRUNCATE TABLE "check" CASCADE;')
    db.execute('TRUNCATE TABLE "apscheduler_jobs" CASCADE;')
    db.commit()


@pytest.fixture(scope='module')
def client() -> Generator:
    with TestClient(app) as c:
        yield c
