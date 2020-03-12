#!/bin/bash

set -e

echo -e "Running $FLASK_ENV Configurations\n*****************\n"

if [[ $FLASK_RUN_MIGRATION -eq 1 ]]; then
  echo -e "Running Migrations\n************\n"
  exec flask db upgrade &
  wait $!
  echo Running migrations job exited with status $?
fi

if [[ $FLASK_ENV == "development" ]]; then
  echo -e "Starting development server\n***********\n"
  exec flask run --host=0.0.0.0 --port 5000 --reload
elif [[ $FLASK_ENV == "testing" ]]; then
  echo -e "Running tests\n************\n"
  exec flask tests
elif [[ $FLASK_ENV == "production" ]]; then
  echo -e "Starting production server\n************\n"
  exec uwsgi --ini /screen_reporter/uwsgi.ini
else 
  echo -e "Your are running invalid config"
fi
