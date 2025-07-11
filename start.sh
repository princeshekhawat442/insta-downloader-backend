#!/bin/bash

# Activate virtualenv if it exists
if [ -d ".venv" ]; then
  source .venv/bin/activate
fi

# Start your app with gunicorn
python3 -m gunicorn main:app
