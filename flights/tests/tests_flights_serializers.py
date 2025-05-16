from django.test import TestCase
from django.utils import timezone
from airports.models import Airport, Route
from airplanes.models import AirplaneType, Airplane
from flights.models import Flight, Crew
from flights.serializers import (
    FlightSerializer,
    FlightListSerializer,
    FlightCreateSerializer,
    FlightUpdateSerializer,
    FlightDetailSerializer,
    CrewSerializer,
    CrewListSerializer,
)
from airports.serializers import RouteCreateSerializer

from datetime import timedelta


class FlightSerializersTest(TestCase):
    def setUp(self):
        self.source = Airport.objects.create(name="JFK", city="New York", country="USA")
        self.destination = Airport.objects.create(name="LAX", city="Los Angeles", country="USA")
        self.route = Route.objects.create(source=self.source, destination=self.destination, distance=4000)
        self.airplane_type = AirplaneType.objects.create(name="Boeing")
        self.airplane = Airplane.objects.create(name="Boeing 747", rows=10, seats_in_row=6,
                                                airplane_type=self.airplane_type)
        self.crew1 = Crew.objects.create(first_name="John", last_name="Doe", rang="Captain")
        self.crew2 = Crew.objects.create(first_name="Jane", last_name="Smith", rang="Pilot")

        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + timedelta(hours=6),
        )
        self.flight.crew.set([self.crew1, self.crew2])

    def test_flight_serializer(self):
        serializer = FlightSerializer(self.flight)
        data = serializer.data
        self.assertEqual(data["route"], self.route.id)
        self.assertEqual(data["airplane"], self.airplane.id)
        self.assertEqual(len(data["crew"]), 2)

    def test_flight_list_serializer(self):
        serializer = FlightListSerializer(self.flight)
        data = serializer.data
        self.assertEqual(data["airplane"]["id"], self.airplane.id)
        self.assertEqual(data["route"]["id"], self.route.id)

    def test_flight_detail_serializer(self):
        serializer = FlightDetailSerializer(self.flight)
        data = serializer.data
        self.assertIn("airplane", data)
        self.assertIn("route", data)
        self.assertIn("crew", data)

    def test_flight_create_serializer(self):
        route_data = {
            "source": self.source.id,
            "destination": self.destination.id,
            "distance": 4200,
            "flight_number": "AA123"
        }
        airplane2 = Airplane.objects.create(name="Boeing 777", rows=15, seats_in_row=8,
                                            airplane_type=self.airplane_type)
        crew_qs = Crew.objects.all()
        data = {
            "route": route_data,
            "airplane": airplane2.id,
            "crew": [member.id for member in crew_qs],
            "arrival_time": timezone.now() + timedelta(hours=6),
        }
        serializer = FlightCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        flight = serializer.save()
        self.assertEqual(flight.route.distance, 4200)
        self.assertEqual(flight.airplane, airplane2)
        self.assertEqual(set(flight.crew.all()), set(crew_qs))

    def test_flight_update_serializer(self):
        data = {
            "airplane": self.airplane.id,
            "crew": [self.crew1.id],
            "route": self.route.id,
            "arrival_time": timezone.now() + timedelta(hours=7),
            "departure_time": timezone.now(),
        }
        serializer = FlightUpdateSerializer(self.flight, data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        flight = serializer.save()
        self.assertEqual(list(flight.crew.all()), [self.crew1])

    def test_crew_serializer(self):
        serializer = CrewSerializer(self.crew1)
        data = serializer.data
        self.assertEqual(data["first_name"], "John")
        self.assertEqual(data["last_name"], "Doe")
        self.assertEqual(data["rang"], "Captain")

    def test_crew_list_serializer(self):
        serializer = CrewListSerializer(self.crew1)
        data = serializer.data
        self.assertEqual(data["first_name"], "John")
        self.assertIn("flights", data)
