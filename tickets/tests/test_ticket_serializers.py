from django.test import TestCase
from rest_framework.exceptions import ValidationError

from flights.serializers import FlightWithSeatsSerializer
from tickets.models import Ticket, Order
from flights.models import Flight
from airplanes.models import Airplane, AirplaneType
from airports.models import Airport, Route
from users.models import User
from tickets.serializers import (
    OrderSerializer,
    TicketSerializer,
    OrderCreateSerializer,
    TicketCreateSerializer,
    TicketDetailSerializer,
)
from django.utils import timezone
from datetime import timedelta


class BaseSetupTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(email="testuser@test.com")
        self.airplane_type = AirplaneType.objects.create(name="Economy")
        self.airplane = Airplane.objects.create(
            name="Test Plane", rows=10, seats_in_row=6, airplane_type=self.airplane_type
        )
        self.source = Airport.objects.create(name="JFK")
        self.destination = Airport.objects.create(name="LAX")
        self.route = Route.objects.create(
            source=self.source, destination=self.destination, distance=1000
        )
        self.now = timezone.now()
        self.flight = Flight.objects.create(
            airplane=self.airplane,
            route=self.route,
            departure_time=self.now,
            arrival_time=self.now + timedelta(hours=2)
        )
        self.order = Order.objects.create(user=self.user)


class OrderSerializerTest(BaseSetupTestCase):
    def test_order_serializer(self):
        serializer = OrderSerializer(self.order)
        self.assertEqual(serializer.data["user"]["email"], "testuser@test.com")


class TicketSerializerTest(BaseSetupTestCase):
    def test_ticket_serializer(self):
        ticket = Ticket.objects.create(row=1, seat=1, flight=self.flight, order=self.order)
        serializer = TicketSerializer(ticket)
        self.assertEqual(serializer.data["row"], 1)
        self.assertEqual(serializer.data["seat"], 1)


class OrderCreateSerializerTest(BaseSetupTestCase):
    def test_order_create_serializer(self):
        data = {
            "tickets": [
                {"row": 1, "seat": 1, "flight": self.flight.id}
            ]
        }
        serializer = OrderCreateSerializer(
            data=data, context={"request": type("Request", (), {"user": self.user})}
        )
        self.assertTrue(serializer.is_valid())
        order = serializer.save()
        self.assertEqual(order.user, self.user)


class TicketCreateSerializerTest(BaseSetupTestCase):
    def test_ticket_create_serializer_valid(self):
        data = {"row": 5, "seat": 3, "flight": self.flight.id}
        serializer = TicketCreateSerializer(
            data=data, context={"request": type("Request", (), {"user": self.user})}
        )
        self.assertTrue(serializer.is_valid())

    def test_ticket_create_serializer_invalid_seat(self):
        data = {"row": 5, "seat": 7, "flight": self.flight.id}
        serializer = TicketCreateSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)


class FlightWithSeatsSerializerTest(BaseSetupTestCase):
    def test_flight_with_seats_serializer(self):
        Ticket.objects.create(flight=self.flight, row=1, seat=1, order=self.order)
        serializer = FlightWithSeatsSerializer(self.flight)
        self.assertEqual(serializer.data["available_seats"], 59)

    def test_available_rows(self):
        airplane = Airplane.objects.create(
            name="Test Plane Small", rows=2, seats_in_row=2, airplane_type=self.airplane_type
        )
        source = Airport.objects.create(name="JFK2")
        destination = Airport.objects.create(name="LAX2")
        route = Route.objects.create(source=source, destination=destination, distance=1000)
        flight = Flight.objects.create(
            airplane=airplane,
            route=route,
            departure_time=self.now,
            arrival_time=self.now + timedelta(hours=2)
        )
        Ticket.objects.create(flight=flight, row=1, seat=1, order=self.order)
        serializer = FlightWithSeatsSerializer(flight)
        self.assertEqual(
            serializer.data["available_rows"],
            [{"row": 1, "available_seats": [2]}, {"row": 2, "available_seats": [1, 2]}]
        )


class TickerDetailSerializerTest(BaseSetupTestCase):
    def test_ticket_detail_serializer(self):
        ticket = Ticket.objects.create(flight=self.flight, row=1, seat=1, order=self.order)
        serializer = TicketDetailSerializer(ticket)
        self.assertEqual(serializer.data["airstrip"], "JFK - , ")
