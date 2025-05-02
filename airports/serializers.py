from rest_framework import serializers

from airports.models import Airport, Route


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ["name", "city", "country", "closest_big_city"]
        read_only_fields = ["id"]


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ["source", "destination", "distance", "flight_number"]
