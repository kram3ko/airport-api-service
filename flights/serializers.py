from django.utils import timezone
from rest_framework import serializers

from airplanes.serializers import AirplaneSerializer
from airports.models import Route
from airports.serializers import (
    RouteCreateSerializer,
    RouteListSerializer,
    RouteSerializer,
)
from flights.models import Crew, Flight
from tickets.models import Ticket


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ["id", "first_name", "last_name", "rang"]


class FlightSerializer(serializers.ModelSerializer):
    crew = CrewSerializer(many=True, read_only=True)

    class Meta:
        model = Flight
        fields = ["id", "route", "airplane", "crew", "departure_time", "arrival_time"]
        read_only_fields = ["id", "departure_time", "arrival_time"]


class FlightListSerializer(serializers.ModelSerializer):
    crew = CrewSerializer(many=True, read_only=True)
    route = RouteSerializer(many=False, read_only=True)
    airplane = AirplaneSerializer(many=False, read_only=True)

    class Meta:
        model = Flight
        fields = ["id", "route", "airplane", "departure_time", "arrival_time", "crew"]
        read_only_fields = ["id"]


class FlightDetailSerializer(FlightSerializer):
    route = RouteListSerializer(many=False, read_only=True)
    airplane = AirplaneSerializer(many=False, read_only=True)
    crew = CrewSerializer(many=True, read_only=True)


class FlightCreateSerializer(serializers.ModelSerializer):
    route = RouteCreateSerializer(many=False)
    crew = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Crew.objects.all(), required=False
    )
    departure_time = serializers.DateTimeField(
        required=False,
        help_text="If not provided, the departure time will be set to now",
    )
    arrival_time = serializers.DateTimeField(required=True)

    class Meta:
        model = Flight
        fields = ["id", "route", "airplane", "crew", "departure_time", "arrival_time"]

    def create(self, validated_data):
        route_data = validated_data.pop("route")
        route = Route.objects.create(**route_data)
        validated_data["route"] = route
        if "departure_time" not in validated_data:
            validated_data["departure_time"] = timezone.now()
        return super().create(validated_data)


class FlightUpdateSerializer(serializers.ModelSerializer):
    crew = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Crew.objects.all(), required=False
    )
    departure_time = serializers.DateTimeField(
        required=False,
        help_text="If not provided, the departure time will be set to now",
    )

    class Meta:
        model = Flight
        fields = ["id", "airplane", "crew", "route", "departure_time", "arrival_time"]


class FlightWithSeatsSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying a flight with available rows and seats
    """

    source = serializers.CharField(
        source="route.source.name",
        read_only=True,
    )
    destination = serializers.CharField(
        source="route.destination.name",
        read_only=True,
    )
    departure_date = serializers.DateTimeField(
        source="departure_time",
        read_only=True,
    )
    available_seats = serializers.SerializerMethodField(
        read_only=True,
    )
    available_rows = serializers.SerializerMethodField(
        read_only=True,
    )

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
        booked_seats = set(Ticket.objects.filter(flight=obj).values_list("row", "seat"))

        rows_with_seats = {}

        for row in range(1, obj.airplane.rows + 1):
            available_seats = []
            for seat in range(1, obj.airplane.seats_in_row + 1):
                if (row, seat) not in booked_seats:
                    available_seats.append(seat)

            if available_seats:
                rows_with_seats[row] = available_seats
        result = []
        for row, seats in rows_with_seats.items():
            result.append({"row": row, "available_seats": seats})

        return result


class CrewListSerializer(serializers.ModelSerializer):
    flights = FlightSerializer(many=True, read_only=True)

    class Meta:
        model = Crew
        fields = ["id", "first_name", "last_name", "rang", "flights"]
        read_only_fields = ["id"]
