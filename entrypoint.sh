#!/bin/bash
set -e

echo "Waiting for database to be ready..."
until python -c "
import sys, os
import psycopg2
try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    conn.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
"; do
  echo "  DB not ready yet, retrying in 2s..."
  sleep 2
done

echo "Running database migrations..."
alembic upgrade head

echo "Starting application..."
exec "$@"
