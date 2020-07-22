"""
URL Routes for this app.
"""
from django.conf.urls import url
from .views import DemographicsStatusView  ##, UserDemographicsView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register(r'user', UserDemographicsView, basename='user_demographics')

urlpatterns = [
    url(
        r'^demographics/status/$',
        DemographicsStatusView.as_view(),
        name='demographics_status'
    ),
    # router.urls,
]
