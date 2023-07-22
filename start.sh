#!/bin/bash
redis-server --daemonize yes
gunicorn -w 4 -b 0.0.0.0:8000 app:app
