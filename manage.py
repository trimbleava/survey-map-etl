#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# To setup and run
# .env to be set
# heath_lsa-# create user heath_lsa_admin with password 'heath_lsa_pass'
# D:\PROJECTS\PY-ENV\Scripts\activate.bat
# (env) pip install django-bootstrap-v5    # installs Bootstrap version 5
# INSTALLED_APPS = 'bootstrap5'
# (env) python manage.py makemigrations
# (env) python manage.py migrate_schemas --shared
# (env) python manage.py createsuperuser --> cciadmin/ccipass
# (env) python manage.py collectstatic -- optional for dev_settings without use of compress!
# (env) python manage.py compress
# (env) $ python manage.py runserver public.lsa.etl.heathus.com:8000 | 127.0.0.1:8000 | 


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "heath_lsa.setting_dir.dev_settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)




if __name__ == "__main__":
    main()
