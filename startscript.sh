#!/bin/bash
# export dbinfo=/config/main.db
# export watchpath=/watch
export dbinfo=/data/debrid-bridge/config/main.db
export watchpath=/data/aria2/torrents
exec gunicorn --bind 0.0.0.0:5000 mainwebui:app
