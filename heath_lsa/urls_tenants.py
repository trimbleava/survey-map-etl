from django.contrib import admin
from django.urls import path, include
from django.conf import settings


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    path('admin/doc/', include('django.contrib.admindocs.urls')),

    # app
    path('', include('tenants.urls')),   # path("chat/", include("chat.urls")), 
    path('', include('customers.urls')),
    path('', include('accounts.urls')),
      
]