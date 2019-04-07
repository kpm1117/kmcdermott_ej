from django.urls import path

from . import views

app_name = "cusip_lookup"
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
]
