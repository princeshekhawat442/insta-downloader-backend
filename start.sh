#!/bin/bash

# Use the virtual environment Render provides
source /opt/render/project/src/.venv/bin/activate

# Start the app
gunicorn main:app
