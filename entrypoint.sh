#!/bin/bash

set -e

echo -e "Running $FLASK_CONFIG Configurations\n*****************\n"

if [ $FLASK_CONFIG = 'DEV' ]; then
  echo -e "Starting development server\n***********\n"
  exec flask run --host=0.0.0.0 --port 5000 --reload
elif [ $FLASK_CONFIG = 'TEST' ]; then
  echo -e "Running tests\n************\n"
  exec flask tests
else
  echo -e "Starting production server\n************\n"
  exec uwsgi --ini /screen_reporter/uwsgi.ini
fi
