from django.urls import path, include
from rest_framework import routers

from flights.views import FlightViewSet, CrewViewSet

app_name = "flights"

router = routers.DefaultRouter()
router.register("flights", FlightViewSet, basename="flights")
router.register("crew", CrewViewSet, basename="crew")

urlpatterns = [
    path("", include(router.urls)),
]
