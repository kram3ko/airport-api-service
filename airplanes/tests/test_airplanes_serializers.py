from rest_framework.test import APITestCase
from airplanes.models import AirplaneType, Airplane
from airplanes.serializers import (
    AirplaneTypeSerializer,
    AirplaneTypeDetailSerializer,
    AirplaneSerializer,
    AirplaneCreateSerializer, AirplaneTypeListSerializer,
)


class AirplaneTypeSerializerTest(APITestCase):
    def test_airplane_type_serializer(self):
        airplane_type = AirplaneType.objects.create(
            name="Boeing 747", category=AirplaneType.AirplaneCategory.PASSENGER
        )
        serializer = AirplaneTypeSerializer(airplane_type)
        self.assertEqual(serializer.data["name"], "Boeing 747")
        self.assertEqual(serializer.data["category"], "Passenger")


class AirplaneTypeDetailSerializerTest(APITestCase):
    def test_airplane_type_detail_serializer(self):
        airplane_type = AirplaneType.objects.create(
            name="Airbus A320", category=AirplaneType.AirplaneCategory.CARGO
        )
        Airplane.objects.create(
            name="Cargo Plane 1", rows=10, seats_in_row=5, airplane_type=airplane_type
        )
        serializer = AirplaneTypeDetailSerializer(airplane_type)
        self.assertEqual(len(serializer.data["airplanes"]), 1)
        self.assertEqual(serializer.data["airplanes"][0]["name"], "Cargo Plane 1")


class AirplaneSerializerTest(APITestCase):
    def test_airplane_serializer(self):
        airplane_type = AirplaneType.objects.create(
            name="Boeing 737", category=AirplaneType.AirplaneCategory.PRIVATE
        )
        airplane = Airplane.objects.create(
            name="Private Jet", rows=5, seats_in_row=4, airplane_type=airplane_type
        )
        serializer = AirplaneSerializer(airplane)
        self.assertEqual(serializer.data["name"], "Private Jet")
        self.assertEqual(serializer.data["total_seats"], 20)


class AirplaneCreateSerializerTest(APITestCase):
    def test_airplane_create_serializer(self):
        airplane_type = AirplaneType.objects.create(
            name="Boeing 777", category=AirplaneType.AirplaneCategory.PASSENGER
        )
        data = {
            "name": "New Plane",
            "rows": 15,
            "seats_in_row": 6,
            "airplane_type": "Boeing 777",
        }
        serializer = AirplaneCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        airplane = serializer.save()
        self.assertEqual(airplane.name, "New Plane")
        self.assertEqual(airplane.total_seats, 90)


class AirplaneTypeListSerializerTest(APITestCase):
    def test_airplane_type_list_serializer(self):
        airplane_type = AirplaneType.objects.create(
            name="Boeing 747", category=AirplaneType.AirplaneCategory.PASSENGER
        )
        Airplane.objects.create(
            name="Plane 1", rows=10, seats_in_row=6, airplane_type=airplane_type
        )
        serializer = AirplaneTypeListSerializer(airplane_type)
        self.assertEqual(serializer.data["name"], "Boeing 747")
        self.assertEqual(len(serializer.data["airplanes"]), 1)