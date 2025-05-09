from django.urls import include, path
from rest_framework import routers

from airplanes.views import AirplaneTypeViewSet, AirplaneViewSet

app_name = "airplanes"

router = routers.DefaultRouter()
router.register("", AirplaneViewSet, basename="airplanes")
router.register("airplane-types", AirplaneTypeViewSet, basename="airplane-types")
urlpatterns = [path("", include(router.urls))]
