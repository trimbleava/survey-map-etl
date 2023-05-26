from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from djgeojson.views import GeoJSONLayerView

# app modules
from tenants.views import TenantHomeView, region_view
from tenants.views import CreateOverlayView, DeleteOverlayView, CreateOverlayLegendView 
from tenants.views import CreateSurveyMapView, DisplaySurveyMapView
from tenants.views import FileUploadView


urlpatterns = [
    path('', TenantHomeView.as_view(), name="home-tenant"),
    path('region/', region_view, name='region'),
    # path("createsurveymap/<str:room_name>", CreateSurveyMapView.as_view(), name="create-survey-map"),
    
    # we may need these in the future - do not delete
    # path("createsurveymap/models/", CreateSurveyMapView.as_view(), name="create-surveymap-models"),
    # path("createsurveymap/migrations/", CreateSurveyMapView.as_view(), name="create-surveymap-migrations"),
    # path("createsurveymap/loaddata/", CreateSurveyMapView.as_view(), name="create-surveymap-loaddata"),
    
    path("createsurveymap/", CreateSurveyMapView.as_view(), name="create-surveymap"),
    path("createoverlay/", CreateSurveyMapView.as_view(), name="create-overlay"),
    path("createovlegend/", CreateOverlayLegendView.as_view(), name="create-ovlegend"),
    path("deleteoverlay/", DeleteOverlayView.as_view(), name="delete-overlay"),
    path("displaysurveymap/", DisplaySurveyMapView.as_view(), name="display-surveymap"),
    path('savesurveyconf/', FileUploadView.as_view(), name="save-survey-config") 
] 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# path('dflow_landbnd.data/', GeoJSONLayerView.as_view(model=models.DflowLandBoundary, properties=('name')), name='dflow_landbnd'),
    