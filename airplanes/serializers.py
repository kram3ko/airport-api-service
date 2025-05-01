from rest_framework import serializers

from airplanes.models import AirplaneType, Airplane


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ["name"]


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ["name", "rows", "seats_in_row", "airplane_type"]
