from rest_framework import serializers

from airports.models import Airport, Route
from base.serializers import IExactCreatableSlugRelatedField


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ["name", "city", "country", "closest_big_city"]
        read_only_fields = ["id"]


class RouteSerializer(serializers.ModelSerializer):
    source = AirportSerializer(read_only=True)
    destination = AirportSerializer(read_only=True)

    class Meta:
        model = Route
        fields = ["source", "destination", "distance", "flight_number"]


class RouteListSerializer(serializers.ModelSerializer):
    Route = RouteSerializer(many=False, read_only=True)

    class Meta:
        model = Route
        fields = ["source", "destination", "Route"]


class RouteCreateSerializer(serializers.ModelSerializer):
    source = IExactCreatableSlugRelatedField(many=True, slug_field="name", queryset=Airport.objects.all())
    destination = IExactCreatableSlugRelatedField(many=True, slug_field="name", queryset=Airport.objects.all())

    class Meta:
        model = Route
        fields = ["source", "destination", "distance", "flight_number"]
        read_only_fields = ["id", "distance", "flight_number"]
