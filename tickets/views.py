from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, never_cache
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from airports.models import Airport
from base.mixins import BaseViewSetMixin
from base.pagination import DefaultPagination
from flights.models import Flight
from tickets.models import Order, Ticket
from tickets.serializers import (
    OrderCreateSerializer,
    OrderDetailSerializer,
    OrderListSerializer,
    OrderSerializer,
    TicketByRouteSerializer,
    TicketDetailSerializer,
    TicketListSerializer,
    TicketSerializer,
)


class OrderViewSet(
    BaseViewSetMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = OrderSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    action_serializers = {
        "list": OrderListSerializer,
        "create": OrderCreateSerializer,
        "retrieve": OrderDetailSerializer,
    }

    @method_decorator(never_cache)
    @method_decorator(cache_page(60 * 60, key_prefix="order-list"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        # Only show current user's orders
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)


class TicketViewSet(
    BaseViewSetMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated]

    action_serializers = {
        "list": TicketListSerializer,
        "retrieve": TicketDetailSerializer,
        "book_by_route": TicketByRouteSerializer,
    }

    def get_queryset(self):
        queryset = Ticket.objects.select_related("flight", "order")
        user = self.request.user
        if not user.is_staff:
            queryset = queryset.filter(order__user=user)
        return queryset.order_by("id")

    @action(detail=False, methods=["get"])
    def booking_info(self, request):
        """
        Retrieve information needed to create a ticket:
        - list of airports
        - list of routes
        - list of upcoming flights
        """
        # Add a list of all airports to the response
        airports = Airport.objects.all()
        airport_data = [{"id": a.id, "name": str(a)} for a in airports]

        # Get a list of available routes
        routes_data = []
        for route in Flight.objects.values(
            "route__source",
            "route__destination",
            "route__source__name",
            "route__destination__name",
        ).distinct():
            routes_data.append(
                {
                    "source_id": route["route__source"],
                    "destination_id": route["route__destination"],
                    "source_name": route["route__source__name"],
                    "destination_name": route["route__destination__name"],
                }
            )

        upcoming_flights = Flight.objects.filter(
            departure_time__gte=timezone.now()
        ).order_by("departure_time")[:10]

        upcoming_flights_data = []
        for flight in upcoming_flights:
            total_seats = flight.airplane.total_seats
            booked_seats_count = Ticket.objects.filter(flight=flight).count()
            available_seats_count = total_seats - booked_seats_count

            upcoming_flights_data.append(
                {
                    "id": flight.id,
                    "source": flight.route.source.name,
                    "destination": flight.route.destination.name,
                    "departure_time": flight.departure_time,
                    "arrival_time": flight.arrival_time,
                    "available_seats": available_seats_count,
                }
            )

        return Response(
            {
                "airports_list": airport_data,
                "routes_list": routes_data,
                "upcoming_flights": upcoming_flights_data,
            }
        )

    @action(detail=False, methods=["post"])
    def book_by_route(self, request):
        """
        Book tickets by specifying a route (source/destination)

        The system will automatically find a suitable flight for the specified route.
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tickets = serializer.save()

        if not isinstance(tickets, (list, tuple)):
            tickets = [tickets]

        return Response(
            {"tickets": TicketListSerializer(tickets, many=True).data},
            status=status.HTTP_201_CREATED,
        )
