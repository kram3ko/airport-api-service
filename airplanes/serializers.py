from rest_framework import serializers

from airplanes.models import AirplaneType, Airplane
from base.serializers import IExactCreatableSlugRelatedField


class AirplaneSerializer(serializers.ModelSerializer):
    airplane_type = IExactCreatableSlugRelatedField(
        slug_field="name", queryset=AirplaneType.objects.all(), required=True
    )

    class Meta:
        model = Airplane
        fields = [
            "id",
            "name",
            "rows",
            "seats_in_row",
            "airplane_type",
            "photo",
            "total_seats",
        ]


class AirplaneTypeSerializer(serializers.ModelSerializer):
    airplanes = AirplaneSerializer(many=True, read_only=True)

    class Meta:
        model = AirplaneType
        fields = ["id", "name", "airplanes"]
