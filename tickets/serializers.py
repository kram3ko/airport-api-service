from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from tickets.models import Ticket, Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "created_at", "user"]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["user"] = request.user
        return super().create(validated_data)


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "flight", "order"]

    def validate(self, data):
        # Get the airplane associated with the flight
        airplane = data["flight"].airplane

        # Validate row and seat limits
        if data["row"] > airplane.rows:
            raise ValidationError(
                f"Row {data['row']} exceeds the maximum rows ({airplane.rows}) for this airplane."
            )
        if data["seat"] > airplane.seats_in_row:
            raise ValidationError(
                f"Seat {data['seat']} exceeds the maximum seats per row ({airplane.seats_in_row}) for this airplane."
            )
        return data
