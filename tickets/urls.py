from django.urls import path, include
from rest_framework import routers

from tickets.views import TicketViewSet, OrderViewSet

app_name = "tickets"

router = routers.DefaultRouter()
router.register("tickets", TicketViewSet, basename="tickets")
router.register("orders", OrderViewSet, basename="orders")

urlpatterns = [path("", include(router.urls))]
