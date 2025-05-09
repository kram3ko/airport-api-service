from django.test import TestCase
from airplanes.models import AirplaneType, Airplane


class AirplaneTypeModelTest(TestCase):
    def test_create_airplane_type(self):
        airplane_type = AirplaneType.objects.create(
            name="Boeing 747", category=AirplaneType.AirplaneCategory.PASSENGER
        )
        self.assertEqual(str(airplane_type), "Boeing 747 - cat: Passenger")
        self.assertEqual(airplane_type.category, "Passenger")


class AirplaneModelTest(TestCase):
    def test_create_airplane(self):
        airplane_type = AirplaneType.objects.create(
            name="Boeing 747", category=AirplaneType.AirplaneCategory.PASSENGER
        )
        airplane = Airplane.objects.create(
            name="Test Airplane",
            rows=10,
            seats_in_row=6,
            airplane_type=airplane_type,
        )
        self.assertEqual(str(airplane), "Test Airplane")
        self.assertEqual(airplane.total_seats, 60)
        self.assertEqual(airplane.airplane_type.name, "Boeing 747")