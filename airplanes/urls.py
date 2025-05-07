from django.urls import path, include
from rest_framework import routers

from airplanes.views import AirplaneViewSet, AirplaneTypeViewSet

app_name = "airplanes"

router = routers.DefaultRouter()
router.register("", AirplaneViewSet, basename="airplanes")
router.register("airplane-types", AirplaneTypeViewSet, basename="airplane-types")
urlpatterns = [path("", include(router.urls))]
