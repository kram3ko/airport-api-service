from rest_framework import serializers

from airports.models import Airport, Route


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ["id", "name", "city", "country", "closest_big_city"]


class RouteSerializer(serializers.ModelSerializer):
    source = AirportSerializer(read_only=True)
    destination = AirportSerializer(read_only=True)
    source_id = serializers.PrimaryKeyRelatedField(
        queryset=Airport.objects.all(), source="source", write_only=True
    )
    destination_id = serializers.PrimaryKeyRelatedField(
        queryset=Airport.objects.all(), source="destination", write_only=True
    )

    class Meta:
        model = Route
        fields = [
            "id",
            "source",
            "destination",
            "source_id",
            "destination_id",
            "distance",
            "flight_number",
        ]

    def validate(self, data):
        if data.get("source") == data.get("destination"):
            raise serializers.ValidationError(
                "Source and destination airports cannot be the same"
            )
        return data


class RouteListSerializer(serializers.ModelSerializer):
    source = AirportSerializer(read_only=True)
    destination = AirportSerializer(read_only=True)

    class Meta:
        model = Route
        fields = ["id", "source", "destination", "distance", "flight_number"]


class RouteCreateSerializer(serializers.ModelSerializer):
    source = serializers.PrimaryKeyRelatedField(queryset=Airport.objects.all())
    destination = serializers.PrimaryKeyRelatedField(queryset=Airport.objects.all())

    class Meta:
        model = Route
        fields = ["source", "destination", "distance", "flight_number"]

    def validate(self, data):
        if data["source"] == data["destination"]:
            raise serializers.ValidationError(
                "Source and destination airports cannot be the same"
            )
        return data


class RouteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ["source", "destination"]
