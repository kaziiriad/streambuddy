#!/bin/bash

# Apply database migrations
echo "Applying database migrations..."
/opt/venv/bin/python app/manage.py migrate

# Start Django development server
echo "Starting Django server..."
exec /opt/venv/bin/python app/manage.py runserver 0.0.0.0:8000