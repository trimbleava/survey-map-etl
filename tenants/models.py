# third party modules
from django.db import models
from django.contrib.gis.db import models as gismodels
from django.contrib.gis.management.commands import ogrinspect


# app modules   
import system_modules as sysm


# # This is an auto-generated Django model module created by ogrinspect.
# class grid_zones(models.Model):
#     gridname = models.CharField(max_length=80)
#     swguid = models.CharField(max_length=80)
#     geom = gismodels.MultiPolygonField(srid=4326)

#     def __str__(self):
#         return self.gridname


# class MainLines(models.Model):
#     installati = models.CharField(max_length=80)
#     diameter = models.FloatField()
#     material = models.BigIntegerField()
#     maintype = models.CharField(max_length=80)
#     swguid = models.CharField(max_length=80)
#     shape_leng = models.FloatField()
#     type = models.CharField(max_length=80)
#     geom = gismodels.MultiLineStringField(srid=4326)

#     def __str__(self):
#         return self.type 


# class ProposedLines(models.Model):
#     status = models.CharField(max_length=80)
#     geom = gismodels.MultiLineStringField(srid=4326)

#     def __str__(self):
#         return self.status 


# class Risers(models.Model):
#     risertype = models.CharField(max_length=80)
#     diameter = models.FloatField()
#     enabled = models.BigIntegerField()
#     swguid = models.CharField(max_length=80)
#     geom = gismodels.MultiPointField(srid=4326)

#     def __str__(self):
#         return self.risertype 


# class ServiceLines(models.Model):
#     installati = models.CharField(max_length=80)
#     diameter = models.FloatField()
#     servicetyp = models.CharField(max_length=80)
#     material = models.BigIntegerField()
#     swguid = models.CharField(max_length=80)
#     shape_leng = models.FloatField()
#     type = models.CharField(max_length=80)
#     geom = gismodels.MultiLineStringField(srid=4326)

#     def __str__(self):
#         return self.type 


class UploadFile(models.Model):
    title = models.CharField(max_length=50, verbose_name=u"Unique Title", unique=True,
                  help_text=u"Enter a unique title", null=True, blank=False)
    filename = models.FileField(verbose_name=u"File Name", help_text=u"Select a file to upload", null=True, blank=False) 
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):         
        return self.title 