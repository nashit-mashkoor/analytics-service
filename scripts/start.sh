#!/bin/sh
cd ./src
# Run database migrations
alembic -c alembic.ini upgrade head

# Seed the database
python seed.py

# Start the application
exec uvicorn main:app --host 0.0.0.0 --port 3000
