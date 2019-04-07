from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('cusip/', include('cusip_lookup.urls'), name='cusip'),
]
