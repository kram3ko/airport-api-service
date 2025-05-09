from django.urls import path, include
from rest_framework.routers import DefaultRouter

from tickets.views import TicketViewSet, OrderViewSet

app_name = "tickets"

router = DefaultRouter()
router.register("tickets", TicketViewSet, basename="ticket")
router.register("orders", OrderViewSet, basename="order")

urlpatterns = [
    path("", include(router.urls)),
]
