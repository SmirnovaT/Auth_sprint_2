#!/bin/bash

cd movies_app
python ./movies_app/manage.py migrate --noinput
python ./movies_app/manage.py collectstatic --no-input
#python ./movies_app/manage.py createsuperuser --noinput || true
cd -

#cd sqlite_to_postgres
#python load_data.py
#cd -

uwsgi --strict --ini /opt/app/uwsgi.ini
