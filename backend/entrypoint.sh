#!/bin/sh

alembic upgrade head

DEPLOY_ENV="${ENV:-dev}"

case $DEPLOY_ENV in
    "dev")
        uvicorn main:app --host 0.0.0.0 --reload
        ;;
    "prod")
        uvicorn main:app --host 0.0.0.0
        ;;
esac