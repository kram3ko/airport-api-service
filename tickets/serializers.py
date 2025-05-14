from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from airports.serializers import RouteSerializer
from flights.serializers import (
    FlightListSerializer,
    FlightSerializer,
    FlightDetailSerializer
)
from tickets.models import Order, Ticket
from users.serializers import UserSerializer


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "created_at", "user"]
        read_only_fields = ["id", "created_at"]


class TicketSerializer(serializers.ModelSerializer):
    flight = FlightSerializer(many=False, read_only=True)

    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "flight", "order"]


class TicketToOrderSerializer(serializers.ModelSerializer):
    flight = serializers.SlugRelatedField(source="flight.airplane", slug_field="name", read_only=True)
    route = RouteSerializer(source="flight.route", read_only=True)

    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "flight", "route"]


class OrderListSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="email", read_only=True)
    tickets = TicketToOrderSerializer(many=True, read_only=True)
    flight = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = ["id", "created_at", "user", "tickets", "flight"]
        read_only_fields = ["id", "created_at", "user"]


class OrderDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    tickets = TicketToOrderSerializer(many=True, read_only=True)
    flight = FlightDetailSerializer(many=False, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "created_at", "user", "tickets", "flight"]
        read_only_fields = ["id", "created_at", "user"]


class TicketListSerializer(serializers.ModelSerializer):
    order = OrderSerializer(many=False, read_only=True)
    flight = FlightListSerializer(many=False, read_only=True)

    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "flight", "order"]
        read_only_fields = ["id", "order"]


class TicketDetailSerializer(serializers.ModelSerializer):
    flight = FlightListSerializer(many=False, read_only=True)
    order = OrderSerializer(many=False, read_only=True)
    airstrip = serializers.CharField(source="flight.route.source", read_only=True)

    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "flight", "order", "airstrip"]
        read_only_fields = ["id", "order"]


class TicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "flight"]

    def validate(self, data):
        flight = data.get("flight")
        row = data.get("row")
        seat = data.get("seat")
        if flight.airplane.seats_in_row < seat:
            raise ValidationError("Invalid seat number")
        if flight.airplane.rows < row:
            raise ValidationError("Invalid row number")
        return data


class TicketByRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "flight"]

    def validate(self, data):
        flight = data.get("flight")
        row = data.get("row")
        seat = data.get("seat")
        if flight.airplane.seats_in_row < seat:
            raise ValidationError("Invalid seat number")
        if flight.airplane.rows < row:
            raise ValidationError("Invalid row number")
        return data

    def create(self, validated_data):
        with transaction.atomic():
            request = self.context.get("request")
            user = request.user
            order = Order.objects.create(user=user)
            validated_data["order"] = order
            return super().create(validated_data)


class OrderCreateSerializer(serializers.ModelSerializer):
    tickets = TicketCreateSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = ["id", "user", "tickets"]
        read_only_fields = ["id", "user", "tickets"]

    def create(self, validated_data):
        with transaction.atomic():
            request = self.context.get("request")
            if request and hasattr(request, "user"):
                validated_data["user"] = request.user
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order
