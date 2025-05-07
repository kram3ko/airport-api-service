from rest_framework import serializers
from django.utils import timezone

from airplanes.serializers import AirplaneSerializer
from airports.models import Route
from airports.serializers import (
    RouteSerializer,
    RouteCreateSerializer,
    RouteListSerializer,
    RouteUpdateSerializer,
)
from flights.models import Flight, Crew


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
    arrival_time = serializers.DateTimeField(required=True)

    class Meta:
        model = Flight
        fields = ["id", "airplane", "crew", "departure_time", "arrival_time"]


class CrewListSerializer(serializers.ModelSerializer):
    flights = FlightSerializer(many=True, read_only=True)

    class Meta:
        model = Crew
        fields = ["id", "first_name", "last_name", "rang", "flights"]
        read_only_fields = ["id"]
