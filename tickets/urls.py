from django.urls import path, include
from rest_framework.routers import DefaultRouter

from tickets.views import TicketViewSet, OrderViewSet

app_name = "tickets"

router = DefaultRouter()
router.register("tickets", TicketViewSet, basename="ticket")
router.register("orders", OrderViewSet, basename="order")

# Available URLs for TicketViewSet:
# - /tickets/ - list of tickets
# - /tickets/?flight=1 - seat information for a specific flight
# - /tickets/?source=1&destination=2 - available flights with seat information
# - /tickets/booking_info/ - information for ticket creation
# - /tickets/<id>/flight_seats/ - detailed seat information for a flight
# - /tickets/book_seats/ - seat booking (POST)
# - /tickets/book_by_route/ - route-based booking (POST)

urlpatterns = [
    path("", include(router.urls)),
]
