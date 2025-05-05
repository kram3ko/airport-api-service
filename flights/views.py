from rest_framework import viewsets

from base.mixins import BaseViewSetMixin
from flights.models import Flight, Crew
from flights.serializers import FlightSerializer, CrewSerializer, CrewListSerializer, FlightListSerializer


class CrewViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer

    action_serializers = {
        "list": CrewListSerializer,
    }


class FlightViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer

    action_serializers = {
        "list": FlightListSerializer,
    }
