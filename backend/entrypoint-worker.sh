#!/bin/sh

celery --app tasks.celery_worker worker \
    -l info \
    -Q main \
    -c 1 \
    --uid=nobody \
    --gid=nogroup
