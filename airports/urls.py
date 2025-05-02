from django.urls import path, include
from rest_framework import routers

from airports.views import AirportViewSet, RouteViewSet

app_name = "airports"

router = routers.DefaultRouter()
router.register("airports", AirportViewSet, basename="airports")
router.register("routes", RouteViewSet, basename="routes")

urlpatterns = [path("", include(router.urls))]
