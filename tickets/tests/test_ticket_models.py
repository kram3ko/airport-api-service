from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
import datetime

from airports.models import Airport, Route
from airplanes.models import Airplane, AirplaneType
from flights.models import Flight
from tickets.models import Ticket, Order

User = get_user_model()


class TicketModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            password="testpassword", email="test@example.com"
        )

        self.source_airport = Airport.objects.create(
            name="Source Airport", city="Source City", country="Source Country"
        )
        self.destination_airport = Airport.objects.create(
            name="Destination Airport",
            city="Destination City",
            country="Destination Country",
        )

        self.route = Route.objects.create(
            source=self.source_airport,
            destination=self.destination_airport,
            distance=1000,
            flight_number="TEST123",
        )

        self.airplane_type = AirplaneType.objects.create(
            name="Test Type", category=AirplaneType.AirplaneCategory.PASSENGER
        )

        self.airplane = Airplane.objects.create(
            name="Test Airplane",
            rows=10,
            seats_in_row=6,
            airplane_type=self.airplane_type,
        )

        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.now() + datetime.timedelta(days=1),
            arrival_time=timezone.now() + datetime.timedelta(days=1, hours=2),
        )

        self.order = Order.objects.create(user=self.user)

        self.ticket = Ticket.objects.create(
            row=1, seat=1, flight=self.flight, order=self.order
        )

    def test_ticket_creation(self):
        self.assertEqual(self.ticket.row, 1)
        self.assertEqual(self.ticket.seat, 1)
        self.assertEqual(self.ticket.flight, self.flight)
        self.assertEqual(self.ticket.order, self.order)

    def test_ticket_string_representation(self):
        expected_string = (
            f"Ticket {self.ticket.id} for Flight {self.flight} (Row: {self.ticket.row}, Seat: {self.ticket.seat})"
        )
        self.assertEqual(str(self.ticket), expected_string)