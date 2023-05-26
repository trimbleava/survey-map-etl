# accounts/models.py
from django.db import models
from tenant_users.tenants.models import UserProfile
from django.utils.translation import gettext_lazy as _

# app modules


class TenantUser(UserProfile):
    name = models.CharField(
        _("Tenant User Name"),
        max_length = 100,
        blank = True,
    )
    