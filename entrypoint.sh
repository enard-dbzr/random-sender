#!/bin/bash

set -e

echo "Applying migrations..."
alembic upgrade head

echo "Starting Gunicorn..."
gunicorn -c gunicorn.conf.py app:app
