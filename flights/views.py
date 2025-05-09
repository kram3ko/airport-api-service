from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated

from base.mixins import BaseViewSetMixin
from base.pagination import DefaultPagination
from flights.models import Flight, Crew
from flights.serializers import (
    FlightSerializer,
    CrewSerializer,
    CrewListSerializer,
    FlightListSerializer,
    FlightCreateSerializer,
    FlightDetailSerializer,
    FlightUpdateSerializer,
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
    }
