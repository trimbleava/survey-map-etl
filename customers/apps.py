from __future__ import unicode_literals
from django.apps import AppConfig


class CustomersConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "customers"

    def ready(self):
        import customers.handlers