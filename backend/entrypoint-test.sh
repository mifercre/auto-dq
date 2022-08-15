#!/bin/sh

alembic upgrade head

pytest tests
