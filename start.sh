#!/bin/bash

# Activate virtual environment
source /opt/render/project/src/.venv/bin/activate

# Start both Flask apps in background and foreground
gunicorn main:app --bind 0.0.0.0:8080 &  # backend
gunicorn bot:app --bind 0.0.0.0:10000    # telegram bot
