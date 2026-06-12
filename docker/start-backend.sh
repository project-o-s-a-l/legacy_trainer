#!/bin/sh
set -eu

until python -m backend.init_db; do
    echo "Database is not ready yet, retrying..."
    sleep 2
done

if [ "${SEED_REFACTOR_TASKS_ON_STARTUP:-false}" = "true" ]; then
    python -m backend.scripts.seed_refactor_tasks
fi

exec uvicorn backend.app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --ssl-keyfile /app/certs/localhost-key.pem \
    --ssl-certfile /app/certs/localhost.pem
