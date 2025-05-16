from django.urls import include, path
from rest_framework.routers import DefaultRouter

from airports.views import AirportViewSet, RouteViewSet

router = DefaultRouter()
router.register("airports", AirportViewSet, basename="airport")
router.register("routes", RouteViewSet, basename="route")

app_name = "airports"

urlpatterns = [
    path("", include(router.urls)),
]
