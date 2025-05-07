from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
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

        # Create airports
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
            f"Ticket {self.ticket.id} for Flight {self.flight} (Row: 1, Seat: 1)"
        )
        self.assertEqual(str(self.ticket), expected_string)


class TicketAPITests(APITestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            password="testpassword", email="test@example.com"
        )
        self.client.force_authenticate(user=self.user)

        # Create airports
        self.source_airport = Airport.objects.create(
            name="Source Airport", city="Source City", country="Source Country"
        )
        self.destination_airport = Airport.objects.create(
            name="Destination Airport",
            city="Destination City",
            country="Destination Country",
        )

        # Create route
        self.route = Route.objects.create(
            source=self.source_airport,
            destination=self.destination_airport,
            distance=1000,
            flight_number="TEST123",
        )

        # Create airplane type
        self.airplane_type = AirplaneType.objects.create(
            name="Test Type", category=AirplaneType.AirplaneCategory.PASSENGER
        )

        # Create airplane
        self.airplane = Airplane.objects.create(
            name="Test Airplane",
            rows=10,
            seats_in_row=6,
            airplane_type=self.airplane_type,
        )

        # Create flight
        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.now() + datetime.timedelta(days=1),
            arrival_time=timezone.now() + datetime.timedelta(days=1, hours=2),
        )

        # Create order
        self.order = Order.objects.create(user=self.user)

        # Create ticket
        self.ticket = Ticket.objects.create(
            row=1, seat=1, flight=self.flight, order=self.order
        )

    def test_list_tickets(self):
        url = reverse("ticket-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_create_ticket(self):
        url = reverse("ticket-list")
        data = {
            "row": 2,
            "seat": 2,
            "route": {
                "source": self.source_airport.id,
                "destination": self.destination_airport.id,
            },
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ticket.objects.count(), 2)

    def test_create_ticket_seat_already_booked(self):
        url = reverse("ticket-list")
        data = {
            "row": 1,  # Already booked in setUp
            "seat": 1,  # Already booked in setUp
            "route": {
                "source": self.source_airport.id,
                "destination": self.destination_airport.id,
            },
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_by_route_endpoint(self):
        url = reverse("ticket-by-route")
        data = {
            "source": self.source_airport.id,
            "destination": self.destination_airport.id,
        }
        response = self.client.get(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # One flight found
        self.assertEqual(response.data[0]["flight_id"], self.flight.id)
        self.assertEqual(response.data[0]["available_seats"], 59)  # 60 total - 1 booked

    def test_available_seats_endpoint(self):
        url = reverse("ticket-available-seats", args=[self.flight.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["flight_id"], self.flight.id)
        self.assertEqual(len(response.data["booked_seats"]), 1)  # One seat booked
        self.assertEqual(
            len(response.data["available_seats"]), 59
        )  # 60 total - 1 booked

    def test_create_multiple_tickets(self):
        url = reverse("ticket-create-multiple")
        data = {
            "flight_id": self.flight.id,
            "seats": [{"row": 2, "seat": 3}, {"row": 2, "seat": 4}],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 2)  # Two tickets created
        self.assertEqual(Ticket.objects.count(), 3)  # 1 from setup + 2 new ones

        # Check that the tickets were created with the right seats
        created_seats = [
            (ticket.row, ticket.seat)
            for ticket in Ticket.objects.filter(flight=self.flight).exclude(
                id=self.ticket.id
            )
        ]
        self.assertIn((2, 3), created_seats)
        self.assertIn((2, 4), created_seats)

    def test_create_multiple_tickets_invalid_seat(self):
        url = reverse("ticket-create-multiple")
        data = {
            "flight_id": self.flight.id,
            "seats": [
                {"row": 1, "seat": 1},  # Already booked
                {"row": 2, "seat": 3},
            ],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Ticket.objects.count(), 1)  # No new tickets created

    def test_available_rows_endpoint(self):
        url = reverse("ticket-available-rows")
        response = self.client.get(f"{url}?flight_id={self.flight.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["flight_id"], self.flight.id)
        self.assertEqual(
            len(response.data["rows_with_seats"]), 10
        )  # 10 rows in airplane

        # Check that the first row has only 5 available seats (one is occupied from setUp)
        first_row = next(r for r in response.data["rows_with_seats"] if r["row"] == 1)
        self.assertEqual(
            len(first_row["available_seats"]), 5
        )  # 6 seats in the row - 1 occupied = 5

        def test_simple_ticket_creation(self):
            url = reverse("ticket-list")
            data = {"flight_id": self.flight.id, "seat": 2}
            response = self.client.post(url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(Ticket.objects.count(), 2)  # 1 from setUp + 1 new

            # Check that the ticket was created with the correct seat
            ticket = Ticket.objects.exclude(id=self.ticket.id).first()
            self.assertEqual(ticket.seat, 2)
            self.assertEqual(ticket.flight, self.flight)

        def test_simple_ticket_creation_with_seats_list(self):
            url = reverse("ticket-list")
            data = {"flight_id": self.flight.id, "seats": [2]}
            response = self.client.post(url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(Ticket.objects.count(), 2)  # 1 from setUp + 1 new

            # Check that the ticket was created with the correct seat
            ticket = Ticket.objects.exclude(id=self.ticket.id).first()
            self.assertEqual(ticket.seat, 2)
            self.assertEqual(ticket.flight, self.flight)

        def test_ticket_creation_same_seat_different_row(self):
            # Pre-create a ticket with seat 2 in row 1
            Ticket.objects.create(flight=self.flight, row=1, seat=2, order=self.order)

            # Now try to create another ticket for seat 2
            url = reverse("ticket-list")
            data = {"flight_id": self.flight.id, "seat": 2}
            response = self.client.post(url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            # Check that the ticket was created in a different row
            created_ticket = Ticket.objects.latest("id")
            self.assertEqual(created_ticket.seat, 2)  # Same seat
            self.assertNotEqual(created_ticket.row, 1)  # But not in the first row

        def test_automatic_seat_selection(self):
            # Fill all seats with number 3 in all rows
            for row in range(1, self.flight.airplane.rows + 1):
                Ticket.objects.create(flight=self.flight, row=row, seat=3, order=self.order)

            # Now try to create a ticket with seat 3
            url = reverse("ticket-list")
            data = {"flight_id": self.flight.id, "seat": 3}
            response = self.client.post(url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            # Check that the ticket was created with a different seat number
            created_ticket = Ticket.objects.latest("id")
            self.assertNotEqual(created_ticket.seat, 3)  # Not seat 3

        def test_multiple_seats_creation(self):
            url = reverse("ticket-list")
            data = {"flight_id": self.flight.id, "seats": [2, 3, 4]}
            response = self.client.post(url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(Ticket.objects.count(), 4)  # 1 from setUp + 3 new

            # Check that all tickets were created with the correct seats
            created_tickets = Ticket.objects.exclude(id=self.ticket.id).order_by("seat")
            self.assertEqual(created_tickets.count(), 3)

            # Check that the seats match the requested ones
            self.assertEqual([t.seat for t in created_tickets], [2, 3, 4])

            # Check that all tickets belong to the same order
            order_ids = set(t.order.id for t in created_tickets)
            self.assertEqual(len(order_ids), 1)

        def test_both_seat_and_seats_error(self):
            url = reverse("ticket-list")
            data = {"flight_id": self.flight.id, "seat": 2, "seats": [3, 4]}
            response = self.client.post(url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        def test_no_seat_error(self):
            url = reverse("ticket-list")
            data = {"flight_id": self.flight.id}
            response = self.client.post(url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        def test_flight_seats(self):
            url = reverse("ticket-flight-seats", args=[self.flight.id])
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            # Check that the response contains information about available seats
            self.assertIn("available_rows", response.data)

            # The airplane has 10 rows, one ticket is already booked, so there should be 10 rows
            self.assertEqual(len(response.data["available_rows"]), 10)

        def test_book_specific_seats(self):
            url = reverse("ticket-book-seats")
            data = {
                "flight_id": self.flight.id,
                "seats": [{"row": 2, "seat": 2}, {"row": 3, "seat": 3}],
            }
            response = self.client.post(url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            # Check that 2 new tickets were created
            self.assertEqual(Ticket.objects.count(), 3)  # 1 from setUp + 2 new

            # Check that the seats were booked correctly
            tickets = Ticket.objects.exclude(id=self.ticket.id)
            seats = [(t.row, t.seat) for t in tickets]
            self.assertIn((2, 2), seats)
            self.assertIn((3, 3), seats)

        def test_book_already_taken_seat(self):
            url = reverse("ticket-book-seats")
            data = {
                "flight_id": self.flight.id,
                "seats": [
                    {"row": 1, "seat": 1},  # This seat is already booked in setUp
                    {"row": 2, "seat": 2},
                ],
            }
            response = self.client.post(url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            # Check that no new tickets were created
            self.assertEqual(Ticket.objects.count(), 1)

        def test_book_seats_with_string_format(self):
            """Test booking seats using string format (for HTML forms)"""
            url = reverse("ticket-book-seats")
            data = {"flight_id": self.flight.id, "rows": "2,3", "seat_numbers": "2,3"}
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            # Check that 2 new tickets were created
            self.assertEqual(Ticket.objects.count(), 3)  # 1 from setUp + 2 new

            # Check that the seats were booked correctly
            tickets = Ticket.objects.exclude(id=self.ticket.id)
            seats = [(t.row, t.seat) for t in tickets]
            self.assertIn((2, 2), seats)
            self.assertIn((3, 3), seats)

        def test_book_by_route(self):
            """Test booking tickets by specifying a route instead of a specific flight"""
            url = reverse("ticket-book-by-route")
            data = {
                "source": self.source_airport.id,
                "destination": self.destination_airport.id,
                "rows": "2,3",
                "seat_numbers": "2,3",
            }
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            # Check that 2 new tickets were created
            self.assertEqual(Ticket.objects.count(), 3)  # 1 from setUp + 2 new

            # Check that the tickets were created for the correct flight
            new_tickets = Ticket.objects.exclude(id=self.ticket.id)
            self.assertEqual(new_tickets.first().flight, self.flight)

            # Check that the seats were booked correctly
            seats = [(t.row, t.seat) for t in new_tickets]
            self.assertIn((2, 2), seats)
            self.assertIn((3, 3), seats)

        def test_airports_list_in_ticket_list(self):
            """Test retrieving the list of airports when requesting the ticket list"""
            url = reverse("ticket-list")
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            # Check that the response contains the list of airports
            self.assertIn("airports_list", response.data)
            self.assertEqual(len(response.data["airports_list"]), 2)  # 2 airports from setUp
