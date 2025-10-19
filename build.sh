#!/usr/bin/env bash
set -o 
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate