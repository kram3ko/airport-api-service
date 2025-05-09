from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from base.mixins import BaseViewSetMixin
from base.pagination import DefaultPagination
from flights.models import Crew, Flight
from flights.serializers import (
    CrewListSerializer,
    CrewSerializer,
    FlightCreateSerializer,
    FlightDetailSerializer,
    FlightListSerializer,
    FlightSerializer,
    FlightUpdateSerializer,
    FlightWithSeatsSerializer,
)


class CrewViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer

    action_serializers = {
        "list": CrewListSerializer,
    }


class FlightViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    queryset = Flight.objects.select_related(
        "route",
        "route__source",
        "route__destination",
        "airplane",
        "airplane__airplane_type",
    ).prefetch_related("crew")

    serializer_class = FlightSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    permission_classes = [IsAuthenticated]
    ordering_fields = ["departure_time", "arrival_time"]
    ordering = ["departure_time"]
    filterset_fields = [
        "route__source",
        "route__destination",
    ]
    pagination_class = DefaultPagination

    action_serializers = {
        "list": FlightListSerializer,
        "create": FlightCreateSerializer,
        "retrieve": FlightDetailSerializer,
        "update": FlightUpdateSerializer,
        "partial_update": FlightUpdateSerializer,
        "flight_seats": FlightWithSeatsSerializer,
    }

    @action(detail=True, methods=["get"])
    def flight_seats(self, request, pk=None):
        """
        Retrieve available rows and seats for a flight.
        """
        flight = self.get_object()
        serializer = FlightWithSeatsSerializer(flight)
        return Response(serializer.data)
