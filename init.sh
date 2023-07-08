#!/usr/bin/fish
poetry run gunicorn --workers 4 wsgi:app -t 180 --bind '::' --port 8001
