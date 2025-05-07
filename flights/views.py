from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter

from base.filters import AirplaneFilter
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
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    filterset_class = AirplaneFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering_fields = ["departure_time", "arrival_time"]
    ordering = ["departure_time"]
    search_fields = ["route__source__name", "route__destination__name"]
    pagination_class = DefaultPagination

    action_serializers = {
        "list": FlightListSerializer,
        "create": FlightCreateSerializer,
        "retrieve": FlightDetailSerializer,
        "update": FlightUpdateSerializer,
        "partial_update": FlightUpdateSerializer,
    }
