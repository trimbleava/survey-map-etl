from django.urls import path, reverse

from customers.views import HomeView, AddPublicTenantView, AddTenantView
from customers.views import load_national_bounds_data, MessagPageView

urlpatterns = [
    path('', HomeView.as_view(), name="home-public"),
    path('add-public-customer/', AddPublicTenantView.as_view(), name="add-public-customer"),
    path('add-customer/', AddTenantView.as_view(), name="add-customer"),
    path('nbnd/', load_national_bounds_data, name="load-national-bounds-data"),
    # example: path('nbnd/', LoadNationalBoundsDataView.as_view(), {'title': 'title'}, name="load-national-bounds-data"),
    path('msg/', MessagPageView.as_view(), name="lsa-messages")  
]
