from django.urls import path, include
from rest_framework.routers import DefaultRouter

from airports.views import AirportViewSet, RouteViewSet

router = DefaultRouter()
router.register("", AirportViewSet, basename="airport")
router.register("routes", RouteViewSet, basename="route")

app_name = "airports"

urlpatterns = [
    path("", include(router.urls)),
]
