from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from airports.serializers import RouteCreateSerializer
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
        fields = ["id", "row", "seat", "flight", "order"]
        read_only_fields = ["id", "order"]


class TicketCreateSerializer(serializers.ModelSerializer):
    route = RouteCreateSerializer(write_only=True)
    order = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "order", "route"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        request = self.context.get("request")
        route_data = validated_data.pop("route")
        order = validated_data.pop("order", None)

        # Получаем рейс на основе маршрута
        flight = Flight.objects.filter(
            route__source=route_data["source"],
            route__destination=route_data["destination"]
        ).first()

        if not flight:
            raise ValidationError("Рейс с указанным маршрутом не найден.")

        if order is None:
            order = Order.objects.create(user=request.user)

        return Ticket.objects.create(flight=flight, order=order, **validated_data)

    def validate(self, data):
        row = data.get("row")
        seat = data.get("seat")
        route_data = data.get("route")

        # Проверяем наличие рейса
        flight = Flight.objects.filter(
            route__source=route_data["source"],
            route__destination=route_data["destination"]
        ).first()

        if not flight:
            raise ValidationError("Рейс с указанным маршрутом не найден.")

        if Ticket.objects.filter(flight=flight, row=row, seat=seat).exists():
            raise ValidationError("Это место уже занято.")

        airplane = flight.airplane

        if row > airplane.rows:
            raise ValidationError(
                f"Ряд {row} превышает максимальное количество рядов ({airplane.rows}) для этого самолета."
            )
        if seat > airplane.seats_in_row:
            raise ValidationError(
                f"Место {seat} превышает максимальное количество мест в ряду ({airplane.seats_in_row}) для этого самолета."
            )

        return data
