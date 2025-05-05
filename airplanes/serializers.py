from rest_framework import serializers

from airplanes.models import AirplaneType, Airplane
from base.serializers import IExactCreatableSlugRelatedField


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ["id", "name", "category"]


class AirplaneTypeListSerializer(serializers.ModelSerializer):
    airplanes = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = AirplaneType
        fields = ["id", "name", "category", "airplanes"]


class AirplaneTypeDetailListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ["id", "name", "rows", "seats_in_row", "total_seats"]


class AirplaneTypeDetailSerializer(serializers.ModelSerializer):
    airplanes = AirplaneTypeDetailListSerializer(many=True, read_only=True)

    class Meta:
        model = AirplaneType
        fields = ["id", "name", "category", "airplanes"]


class AirplaneSerializer(serializers.ModelSerializer):
    airplane_type = AirplaneTypeSerializer(many=False, read_only=True)

    class Meta:
        model = Airplane
        fields = [
            "id",
            "name",
            "rows",
            "seats_in_row",
            "total_seats",
            "airplane_type",
            "photo",
        ]


class AirplaneDetailSerializer(AirplaneSerializer):
    airplane_type = AirplaneSerializer(many=False, read_only=True)


class AirplaneCreateSerializer(AirplaneSerializer):
    airplane_type = IExactCreatableSlugRelatedField(
        many=False, queryset=AirplaneType.objects.all(), slug_field="name"
    )
