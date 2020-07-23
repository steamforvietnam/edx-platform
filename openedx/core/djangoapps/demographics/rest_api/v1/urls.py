"""
URL Routes for this app.
"""
from django.conf.urls import url
from .views import DemographicsStatusView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = [
    url(
        r'^demographics/status/$',
        DemographicsStatusView.as_view(),
        name='demographics_status'
    ),
]
