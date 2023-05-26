# routing.py
from django.urls import re_path, path

# app modules
# from tenants.overlay_consumer import OverlayConsumer
from tenants.delete_overlay_consumer import DeleteOverlayConsumer
from tenants.surveymap_consumer import SurveyMapConsumer
from tenants.overlay_consumer import OverlayConsumer

# SurveyMapModelsConsumer, SurveyMapMigrationsConsumer, SurveyMapLoadDataConsumer  keep for future
from tenants.overlaylegend_consumer import OverlayLegendConsumer

websocket_urlpatterns = [
    # re_path(r"ws/op/(?P<room_name>\w+)/$", SurveyMapConsumer.as_asgi()),
    # path("ws/ov/", OverlayConsumer.as_asgi()),

    path("ws/delov/", DeleteOverlayConsumer.as_asgi()),
    path("ws/survey-map/", SurveyMapConsumer.as_asgi()),
    path("ws/overlay-map/", OverlayConsumer.as_asgi()),

    # path("ws/op/models", SurveyMapModelsConsumer.as_asgi()),
    # path("ws/op/migrations", SurveyMapMigrationsConsumer.as_asgi()),
    # path("ws/op/loaddata", SurveyMapLoadDataConsumer.as_asgi())
]
