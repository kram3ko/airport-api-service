from django.test import TestCase
from django.utils import timezone
from airports.models import Airport, Route
from airplanes.models import Airplane, AirplaneType
from flights.models import Crew, Flight
from datetime import timedelta

class FlightModelTest(TestCase):
    def setUp(self):
        self.source = Airport.objects.create(name="JFK", city="New York", country="USA")
        self.destination = Airport.objects.create(name="LAX", city="Los Angeles", country="USA")
        self.route = Route.objects.create(source=self.source, destination=self.destination, distance=4000)
        self.airplane_type = AirplaneType.objects.create(name="Wide-body")
        self.airplane = Airplane.objects.create(
            name="Boeing 747",
            rows=10,
            seats_in_row=6,
            airplane_type=self.airplane_type
        )
        self.crew_member = Crew.objects.create(first_name="John", last_name="Doe", rang="Captain")

    def test_flight_creation(self):
        flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + timedelta(hours=6),
        )
        flight.crew.add(self.crew_member)
        self.assertEqual(flight.route, self.route)
        self.assertEqual(flight.airplane, self.airplane)
        self.assertIn(self.crew_member, flight.crew.all())

    def test_flight_str_representation(self):
        flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + timedelta(hours=6),
        )
        expected_str = f"Flight from {self.route.source} to {self.route.destination} by airplane {self.airplane.name}"
        self.assertEqual(str(flight), expected_str)