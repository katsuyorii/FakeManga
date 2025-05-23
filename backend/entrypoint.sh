#!/bin/bash

echo "Check new migrations..."
alembic upgrade head

echo "Starting web server..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload