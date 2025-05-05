from rest_framework import viewsets

from airports.models import Airport, Route
from airports.serializers import AirportSerializer, RouteSerializer
from base.pagination import DefaultPagination


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    pagination_class = DefaultPagination


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
