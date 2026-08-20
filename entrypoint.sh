#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

echo "=== Starting Hearing App Production Entrypoint Script ==="

# Wait for PostgreSQL database if DB_HOST is set
if [ -n "$DB_HOST" ]; then
    echo "Waiting for PostgreSQL at $DB_HOST:$DB_PORT..."
    while ! nc -z $DB_HOST ${DB_PORT:-5432}; do
      sleep 1
    done
    echo "PostgreSQL is up and accepting connections!"
fi

# Apply Django database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files for Nginx
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Auto-create superuser if DJANGO_SUPERUSER_EMAIL & DJANGO_SUPERUSER_PASSWORD are set
if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Checking/creating default superuser..."
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        email='$DJANGO_SUPERUSER_EMAIL',
        name='${DJANGO_SUPERUSER_NAME:-Admin User}',
        password='$DJANGO_SUPERUSER_PASSWORD'
    )
    print('Superuser created successfully.')
else:
    print('Superuser already exists.')
" || true
fi

# Start Gunicorn WSGI HTTP Server
echo "Starting Gunicorn Production Server..."
exec gunicorn Config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers ${GUNICORN_WORKERS:-3} \
    --threads ${GUNICORN_THREADS:-2} \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level ${LOG_LEVEL:-info}
