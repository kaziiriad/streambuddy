#!/bin/bash

# Start Redis server
redis-server --daemonize yes

# Wait for Redis to be ready
until redis-cli ping; do
  echo "Waiting for Redis to start..."
  sleep 1
done

# Apply database migrations
python manage.py migrate

# Start Celery worker in background
celery -A streambuddy worker --loglevel=info &

# Start Django development server
python manage.py runserver 0.0.0.0:8000