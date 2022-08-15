#!/bin/sh
# wait-for-postgres.sh

set -e

cmd="$@"

until PGPASSWORD=$POSTGRES_PASSWORD psql -h "db" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 3
done

>&2 echo "Postgres is up - executing command: $cmd"
exec $cmd