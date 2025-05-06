from rest_framework import viewsets

from base.mixins import BaseViewSetMixin
from tickets.models import Order, Ticket
from tickets.serializers import (
    OrderSerializer,
    TicketSerializer,
    TicketListSerializer,
    OrderListSerializer,
    TicketCreateSerializer,
    TickerDetailSerializer, OrderCreateSerializer,
)


class OrderViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    action_serializers = {
        "list": OrderListSerializer,
        "create": OrderCreateSerializer,
    }


class TicketViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    action_serializers = {
        "list": TicketListSerializer,
        "create": TicketCreateSerializer,
        "retrieve": TickerDetailSerializer,
        "update": TicketCreateSerializer
    }
    def get_object(self):
        return self.request.user