from rest_framework import viewsets

from airplanes.models import Airplane, AirplaneType
from airplanes.serializers import (
    AirplaneSerializer,
    AirplaneTypeSerializer,
    AirplaneCreateSerializer,
    AirplaneTypeListSerializer,
    AirplaneTypeDetailSerializer,
)

from base.mixins import BaseViewSetMixin
from base.pagination import DefaultPagination


class AirplaneViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
    pagination_class = DefaultPagination

    action_serializers = {
        "create": AirplaneCreateSerializer,
        "update": AirplaneCreateSerializer,
        "partial_update": AirplaneCreateSerializer,
    }


class AirplaneTypeViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer

    action_serializers = {
        "list": AirplaneTypeListSerializer,
        "retrieve": AirplaneTypeDetailSerializer,
    }
