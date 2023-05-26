# from django.contrib.gis import admin  check on this vs below one
from django.contrib import admin
from django_tenants.admin import TenantAdminMixin
from django_tenants.utils import get_public_schema_name
from leaflet.admin import LeafletGeoAdmin

# app modules
from customers.models import Client, Domain
from customers.models import USAStates

#
# Register your models here.
#
# public admin can use admin site to creats tenants
# so, is good to register this model with admin site.
# because this model is a shared model, only authorized
# public admin and not authorized tenant can access.
# however, a tenant admin can be authorized to access
# if invokes the application on public URL.

class DomainInline(admin.TabularInline):
     model = Domain

@admin.register(Client)
class ClientAdmin(TenantAdminMixin, admin.ModelAdmin):
    inlines = [DomainInline]
    list_display = ['name', 'description']


@admin.register(USAStates)
class USAStatesAdmin(LeafletGeoAdmin):
    list_display = ['name', 'awater']