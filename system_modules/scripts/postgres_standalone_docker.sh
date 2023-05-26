#!/bin/bash
# For local development with an standalone dockerized DB
# provide db connection info in this file,
# activate venv
# from command shell: source postgres_standalone_docker.sh
# python manage.py runserver
# db
export DJANGO_DB_ENGINE=django.db.backends.postgresql
export DJANGO_DB_NAME=postgres
export DJANGO_DB_USER=postgres
export DJANGO_DB_PASSWORD=test-password
export DJANGO_DB_HOST=172.17.0.2
export DJANGO_DB_PORT=5432
# mail
export EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
# cache