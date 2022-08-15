from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import crud
from core.config import settings
from models.check import CheckType


def test_create_check_invalid_crontab(
    client: TestClient, db: Session
) -> None:
    data = {
        'name': 'test check invalid crontab',
        'type': CheckType.UNIQUENESS.value,
        'source': 'SELECT 1',
        'database_id': 1,
        'schema_id': 1,
        'table_id': 1,
        'column_id': 1,
        'schedule': '* * * * * *'
    }
    response = client.post(
        f'{settings.API_PREFIX_ADMIN}/checks/', json=data,
    )
    assert response.status_code == 422
    content = response.json()
    assert content['detail'][0]['msg'] == "Invalid 'schedule' cron format"


def test_create_check_freshness(
    client: TestClient, db: Session
) -> None:
    db_test = crud.db.get(db=db, id=1)
    data = {
        'name': 'test check freshness',
        'type': CheckType.FRESHNESS.value,
        'source': 'SELECT 1',
        'database_id': db_test.id,
        'schedule': '* * * * *',
        'delta_threshold_seconds': 10
    }
    response = client.post(
        f'{settings.API_PREFIX_ADMIN}/checks/', json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content['type'] == data['type']
    assert content['source'] == data['source']
    assert content['database_id'] == data['database_id']
    assert 'id' in content
