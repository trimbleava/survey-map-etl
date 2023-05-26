from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_tenants.models import TenantMixin, DomainMixin
from tenant_users.tenants.models import TenantBase
from django.contrib.gis.db import models as gismodels


class Client(TenantBase):    # TenantMixin changed by user tenants app
    name = models.CharField(_('Tenant Name'), max_length=100)  
    description = models.TextField(_('Description'), max_length=200)

    # extras in TenantBase
    # slug = models.SlugField(_('Tenant URL Name'), blank=True)
    # The owner of the tenant. Only they can delete it. This can be changed,
    # but it can't be blank. There should always be an owner.
    # owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,)
    #                                    AUTH_USER_MODEL = 'accounts.TenantUser'
    #
    # TenantUser: id, name, password, email (is used as owner of tenant), is_active, tenants, not abstract
    #
    # Client/Company: id, slug(url), schema_name, name='owner'=FK(to=user), created, modified, not abstract
    # Domain: id, domain, is_primary, tenant=FK(to=Company), not abstract

class Domain(DomainMixin):

    # domain = models.CharField(max_length=253, unique=True, db_index=True)
    # tenant = models.ForeignKey(settings.TENANT_MODEL, db_index=True, related_name='domains',
    #                            on_delete=models.CASCADE)
    # print(tenant)
    # # Set this to true if this is the primary domain
    # is_primary = models.BooleanField(default=True, db_index=True)
    pass

#
# python manage.py ogrinspect TM_WORLD_BORDERS-0.3.shp world_borders --srid=4326 --mapping --multi
# python manage.py ogrinspect D:\PROJECTS\heath_lsa\INPUT\cb_2018_us_state_20m.shp us_states --srid=4326 --mapping --multi
# This is an auto-generated Django model module created by ogrinspect.
# See management command load_gisdata)
#
class USAStates(gismodels.Model):
    statefp = models.CharField(max_length=2)
    statens = models.CharField(max_length=8)
    affgeoid = models.CharField(max_length=11)
    geoid = models.CharField(max_length=2)
    stusps = models.CharField(max_length=2)
    name = models.CharField(max_length=100)
    lsad = models.CharField(max_length=2)
    aland = models.BigIntegerField()
    awater = models.BigIntegerField()
  
    geom = gismodels.MultiPolygonField(srid=4326)

    def __str__(self):
        return self.name
    
    def get_mapping(self):
        # Auto-generated `LayerMapping` dictionary for us_states model
        us_states_mapping = {
            'statefp': 'STATEFP',
            'statens': 'STATENS',
            'affgeoid': 'AFFGEOID',
            'geoid': 'GEOID',
            'stusps': 'STUSPS',
            'name': 'NAME',
            'lsad': 'LSAD',
            'aland': 'ALAND',
            'awater': 'AWATER',
            'geom': 'MULTIPOLYGON',
        }
        return us_states_mapping

    class Meta:
        verbose_name='USA States 2018'
