from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from airplanes.models import AirplaneType, Airplane
from airports.models import Airport, Route
from flights.models import Flight
from tickets.models import Ticket, Order

User = get_user_model()


class TicketViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@test.com", password="password")
        self.staff_user = User.objects.create_user(email="admin@test.com", password="password", is_staff=True)
        self.airport1 = Airport.objects.create(name="JFK", city="New York", country="USA")
        self.airport2 = Airport.objects.create(name="LAX", city="Los Angeles", country="USA")
        self.route = Route.objects.create(source=self.airport1, destination=self.airport2, distance=4000)
        self.airplane_type = AirplaneType.objects.create(name="Boeing")
        self.airplane = Airplane.objects.create(
            name="Boeing 747",
            rows=10,
            seats_in_row=6,
            airplane_type=self.airplane_type
        )
        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.now() + timezone.timedelta(days=1),
            arrival_time=timezone.now() + timezone.timedelta(days=1, hours=6),
        )
        self.order = Order.objects.create(user=self.user)
        self.ticket = Ticket.objects.create(flight=self.flight, row=1, seat=1, order=self.order)

    def test_booking_info(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("tickets:ticket-booking-info")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("airports_list", response.data)
        self.assertIn("routes_list", response.data)
        self.assertIn("upcoming_flights", response.data)

    def test_book_by_route(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("tickets:ticket-book-by-route")
        data = {"row": 2, "seat": 3, "flight": self.flight.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["tickets"]), 1)
        self.assertEqual(response.data["tickets"][0]["row"], 2)
        self.assertEqual(response.data["tickets"][0]["seat"], 3)

    def test_list_tickets(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("tickets:ticket-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_retrieve_ticket(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("tickets:ticket-detail", args=[self.ticket.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["row"], 1)
        self.assertEqual(response.data["seat"], 1)

    def test_create_ticket_invalid_seat(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("tickets:ticket-book-by-route")  # Используем правильный эндпоинт
        data = {"row": 2, "seat": 7, "flight": self.flight.id}  # Invalid seat
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid seat number", str(response.data))
