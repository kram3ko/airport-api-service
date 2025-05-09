from django.urls import include, path
from rest_framework.routers import DefaultRouter

from tickets.views import OrderViewSet, TicketViewSet

app_name = "tickets"

router = DefaultRouter()
router.register("tickets", TicketViewSet, basename="ticket")
router.register("orders", OrderViewSet, basename="order")

urlpatterns = [
    path("", include(router.urls)),
]
