from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from airplanes.serializers import AirplaneSerializer
from airports.models import Airport, Route
from airports.serializers import (
    RouteSerializer,
    RouteListSerializer,
    RouteUpdateSerializer,
)
from flights.models import Flight
from flights.serializers import FlightSerializer, FlightListSerializer
from tickets.models import Ticket, Order
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


class FlightWithSeatsSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying a flight with available rows and seats
    """

    source = serializers.CharField(source="route.source.name", read_only=True)
    destination = serializers.CharField(source="route.destination.name", read_only=True)
    departure_date = serializers.DateTimeField(source="departure_time", read_only=True)
    available_seats = serializers.SerializerMethodField(read_only=True)
    available_rows = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Flight
        fields = [
            "id",
            "source",
            "destination",
            "departure_time",
            "arrival_time",
            "departure_date",
            "available_seats",
            "available_rows",
        ]

    def get_available_seats(self, obj):
        total_seats = obj.airplane.total_seats
        booked_seats = Ticket.objects.filter(flight=obj).count()
        return total_seats - booked_seats

    def get_available_rows(self, obj):
        # Get all booked seats
        booked_seats = set(Ticket.objects.filter(flight=obj).values_list("row", "seat"))

        # Create a dictionary of rows with available seats
        rows_with_seats = {}

        for row in range(1, obj.airplane.rows + 1):
            available_seats = []
            for seat in range(1, obj.airplane.seats_in_row + 1):
                if (row, seat) not in booked_seats:
                    available_seats.append(seat)

            if available_seats:  # Add the row only if it has available seats
                rows_with_seats[row] = available_seats

        # Format the result for usability
        result = []
        for row, seats in rows_with_seats.items():
            result.append({"row": row, "available_seats": seats})

        return result
