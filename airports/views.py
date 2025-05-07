from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from airports.models import Airport, Route
from airports.serializers import (
    AirportSerializer,
    RouteSerializer,
    RouteUpdateSerializer,
)
from base.pagination import DefaultPagination


class AirportViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows airports to be viewed or edited.
    """

    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["city", "country"]
    search_fields = ["name", "city", "country"]
    ordering_fields = ["name", "city", "country"]
    ordering = ["name"]


class RouteViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows routes to be viewed or edited.
    """

    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["source", "destination", "flight_number"]
    search_fields = ["flight_number"]
    ordering_fields = ["distance", "flight_number"]
    ordering = ["flight_number"]

    action_serializers = {
        "update": RouteUpdateSerializer,
        "partial_update": RouteUpdateSerializer,
    }
