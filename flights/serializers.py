from rest_framework import serializers
from django.utils import timezone

from airplanes.serializers import AirplaneSerializer
from airports.serializers import RouteSerializer
from flights.models import Flight, Crew


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ["id", "first_name", "last_name", "rang"]


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ["id", "route", "airplane", "departure_time", "arrival_time", ]

    def create(self, validated_data):
        if "departure_time" not in validated_data:
            validated_data["departure_time"] = timezone.now()
        return super().create(validated_data)


class FlightListSerializer(serializers.ModelSerializer):
    crew = CrewSerializer(many=True, read_only=True)
    route = RouteSerializer(many=False, read_only=True)
    airplane = AirplaneSerializer(many=False, read_only=True)

    class Meta:
        model = Flight
        fields = ["id", "route", "airplane", "departure_time", "arrival_time", "crew"]
        read_only_fields = ["id"]


class CrewListSerializer(serializers.ModelSerializer):
    flights = FlightSerializer(many=True, read_only=True)

    class Meta:
        model = Crew
        fields = ["id", "first_name", "last_name", "rang", "flights"]
        read_only_fields = ["id"]
