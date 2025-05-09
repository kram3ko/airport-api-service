from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from flights.serializers import FlightListSerializer, FlightSerializer
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


class OrderListSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    tickets = TicketSerializer(many=True, read_only=True)
    flight = FlightListSerializer(many=False, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "created_at", "user", "tickets", "flight"]
        read_only_fields = ["id", "created_at", "user"]


class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "user"]
        read_only_fields = ["id", "user"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["user"] = request.user
        return super().create(validated_data)


class TicketListSerializer(serializers.ModelSerializer):
    order = OrderSerializer(many=False, read_only=True)
    flight = FlightListSerializer(many=False, read_only=True)

    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "flight", "order"]
        read_only_fields = ["id", "order"]


class TickerDetailSerializer(serializers.ModelSerializer):
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

    def create(self, validated_data):
        with transaction.atomic():
            request = self.context.get("request")
            user = request.user
            order = Order.objects.create(user=user)
            validated_data["order"] = order
            return super().create(validated_data)
