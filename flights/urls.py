from django.urls import include, path
from rest_framework import routers

from flights.views import CrewViewSet, FlightViewSet

app_name = "flights"

router = routers.DefaultRouter()
router.register("flights", FlightViewSet, basename="flights")
router.register("crew", CrewViewSet, basename="crew")

urlpatterns = [
    path("", include(router.urls)),
]
