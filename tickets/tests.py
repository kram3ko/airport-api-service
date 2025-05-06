# Create your tests here.

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.exceptions import ValidationError
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
        # Create test user
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
            email="test@example.com"
        )
        
        # Create airports
        self.source_airport = Airport.objects.create(
            name="Source Airport",
            city="Source City",
            country="Source Country"
        )
        self.destination_airport = Airport.objects.create(
            name="Destination Airport",
            city="Destination City",
            country="Destination Country"
        )
        
        # Create route
        self.route = Route.objects.create(
            source=self.source_airport,
            destination=self.destination_airport,
            distance=1000,
            flight_number="TEST123"
        )
        
        # Create airplane type
        self.airplane_type = AirplaneType.objects.create(
            name="Test Type",
            category=AirplaneType.AirplaneCategory.PASSENGER
        )
        
        # Create airplane
        self.airplane = Airplane.objects.create(
            name="Test Airplane",
            rows=10,
            seats_in_row=6,
            airplane_type=self.airplane_type
        )
        
        # Create flight
        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.now() + datetime.timedelta(days=1),
            arrival_time=timezone.now() + datetime.timedelta(days=1, hours=2)
        )
        
        # Create order
        self.order = Order.objects.create(user=self.user)
        
        # Create ticket
        self.ticket = Ticket.objects.create(
            row=1,
            seat=1,
            flight=self.flight,
            order=self.order
        )
        
    def test_ticket_creation(self):
        self.assertEqual(self.ticket.row, 1)
        self.assertEqual(self.ticket.seat, 1)
        self.assertEqual(self.ticket.flight, self.flight)
        self.assertEqual(self.ticket.order, self.order)
    
    def test_ticket_string_representation(self):
        expected_string = f"Ticket {self.ticket.id} for Flight {self.flight} (Row: 1, Seat: 1)"
        self.assertEqual(str(self.ticket), expected_string)


class TicketAPITests(APITestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
            email="test@example.com"
        )
        self.client.force_authenticate(user=self.user)
        
        # Create airports
        self.source_airport = Airport.objects.create(
            name="Source Airport",
            city="Source City",
            country="Source Country"
        )
        self.destination_airport = Airport.objects.create(
            name="Destination Airport",
            city="Destination City",
            country="Destination Country"
        )
        
        # Create route
        self.route = Route.objects.create(
            source=self.source_airport,
            destination=self.destination_airport,
            distance=1000,
            flight_number="TEST123"
        )
        
        # Create airplane type
        self.airplane_type = AirplaneType.objects.create(
            name="Test Type",
            category=AirplaneType.AirplaneCategory.PASSENGER
        )
        
        # Create airplane
        self.airplane = Airplane.objects.create(
            name="Test Airplane",
            rows=10,
            seats_in_row=6,
            airplane_type=self.airplane_type
        )
        
        # Create flight
        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.now() + datetime.timedelta(days=1),
            arrival_time=timezone.now() + datetime.timedelta(days=1, hours=2)
        )
        
        # Create order
        self.order = Order.objects.create(user=self.user)
        
        # Create ticket
        self.ticket = Ticket.objects.create(
            row=1,
            seat=1,
            flight=self.flight,
            order=self.order
        )
    
    def test_list_tickets(self):
        url = reverse('ticket-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_ticket(self):
        url = reverse('ticket-list')
        data = {
            'row': 2,
            'seat': 2,
            'route': {
                'source': self.source_airport.id,
                'destination': self.destination_airport.id
            }
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ticket.objects.count(), 2)
    
    def test_create_ticket_seat_already_booked(self):
        url = reverse('ticket-list')
        data = {
            'row': 1,  # Already booked in setUp
            'seat': 1,  # Already booked in setUp
            'route': {
                'source': self.source_airport.id,
                'destination': self.destination_airport.id
            }
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_by_route_endpoint(self):
        url = reverse('ticket-by-route')
        data = {
            'source': self.source_airport.id,
            'destination': self.destination_airport.id
        }
        response = self.client.get(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # One flight found
        self.assertEqual(response.data[0]['flight_id'], self.flight.id)
        self.assertEqual(response.data[0]['available_seats'], 59)  # 60 total - 1 booked
    
    def test_available_seats_endpoint(self):
        url = reverse('ticket-available-seats', args=[self.flight.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['flight_id'], self.flight.id)
        self.assertEqual(len(response.data['booked_seats']), 1)  # One seat booked
        self.assertEqual(len(response.data['available_seats']), 59)  # 60 total - 1 booked
    
    def test_create_multiple_tickets(self):
        url = reverse('ticket-create-multiple')
        data = {
            'flight_id': self.flight.id,
            'seats': [
                {'row': 2, 'seat': 3},
                {'row': 2, 'seat': 4}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 2)  # Two tickets created
        self.assertEqual(Ticket.objects.count(), 3)  # 1 from setup + 2 new ones
        
        # Check that the tickets were created with the right seats
        created_seats = [(ticket.row, ticket.seat) for ticket in Ticket.objects.filter(flight=self.flight).exclude(id=self.ticket.id)]
        self.assertIn((2, 3), created_seats)
        self.assertIn((2, 4), created_seats)
    
    def test_create_multiple_tickets_invalid_seat(self):
        url = reverse('ticket-create-multiple')
        data = {
            'flight_id': self.flight.id,
            'seats': [
                {'row': 1, 'seat': 1},  # Already booked
                {'row': 2, 'seat': 3}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Ticket.objects.count(), 1)  # No new tickets created

    def test_available_rows_endpoint(self):
        url = reverse('ticket-available-rows')
        response = self.client.get(f"{url}?flight_id={self.flight.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['flight_id'], self.flight.id)
        self.assertEqual(len(response.data['rows_with_seats']), 10)  # 10 rows in airplane
        
        # Проверяем, что первый ряд имеет только 5 доступных мест (одно занято из setUp)
        first_row = next(r for r in response.data['rows_with_seats'] if r['row'] == 1)
        self.assertEqual(len(first_row['available_seats']), 5)  # 6 мест в ряду - 1 занятое = 5
        
    def test_simple_ticket_creation(self):
        url = reverse('ticket-list')
        data = {
            'flight_id': self.flight.id,
            'seat': 2
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ticket.objects.count(), 2)  # 1 from setup + 1 new
        
        # Проверяем, что билет создан с правильным местом
        ticket = Ticket.objects.exclude(id=self.ticket.id).first()
        self.assertEqual(ticket.seat, 2)
        self.assertEqual(ticket.flight, self.flight)
        
    def test_simple_ticket_creation_with_seats_list(self):
        url = reverse('ticket-list')
        data = {
            'flight_id': self.flight.id,
            'seats': [2]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ticket.objects.count(), 2)  # 1 from setup + 1 new
        
        # Проверяем, что билет создан с правильным местом
        ticket = Ticket.objects.exclude(id=self.ticket.id).first()
        self.assertEqual(ticket.seat, 2)
        self.assertEqual(ticket.flight, self.flight)
        
    def test_ticket_creation_same_seat_different_row(self):
        # Предварительно создаем билет с местом 2 в ряду 1
        Ticket.objects.create(
            flight=self.flight,
            row=1,
            seat=2,
            order=self.order
        )
        
        # Теперь пытаемся создать еще один билет на место 2
        url = reverse('ticket-list')
        data = {
            'flight_id': self.flight.id,
            'seat': 2
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Проверяем, что билет создан в другом ряду
        created_ticket = Ticket.objects.latest('id')
        self.assertEqual(created_ticket.seat, 2)  # То же место
        self.assertNotEqual(created_ticket.row, 1)  # Но не в первом ряду
        
    def test_automatic_seat_selection(self):
        # Заполняем все места с номером 3 во всех рядах
        for row in range(1, self.flight.airplane.rows + 1):
            Ticket.objects.create(
                flight=self.flight,
                row=row,
                seat=3,
                order=self.order
            )
        
        # Теперь пытаемся создать билет с местом 3
        url = reverse('ticket-list')
        data = {
            'flight_id': self.flight.id,
            'seat': 3
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Проверяем, что билет создан с другим номером места
        created_ticket = Ticket.objects.latest('id')
        self.assertNotEqual(created_ticket.seat, 3)  # Не место 3
        
    def test_multiple_seats_creation(self):
        url = reverse('ticket-list')
        data = {
            'flight_id': self.flight.id,
            'seats': [2, 3, 4]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ticket.objects.count(), 4)  # 1 from setup + 3 new
        
        # Проверяем, что все билеты созданы с правильными местами
        created_tickets = Ticket.objects.exclude(id=self.ticket.id).order_by('seat')
        self.assertEqual(created_tickets.count(), 3)
        
        # Проверяем, что места соответствуют запрошенным
        self.assertEqual([t.seat for t in created_tickets], [2, 3, 4])
        
        # Проверяем, что все билеты принадлежат одному заказу
        order_ids = set(t.order.id for t in created_tickets)
        self.assertEqual(len(order_ids), 1)
        
    def test_both_seat_and_seats_error(self):
        url = reverse('ticket-list')
        data = {
            'flight_id': self.flight.id,
            'seat': 2,
            'seats': [3, 4]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_no_seat_error(self):
        url = reverse('ticket-list')
        data = {
            'flight_id': self.flight.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_flight_seats(self):
        url = reverse('ticket-flight-seats', args=[self.flight.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем, что получили информацию о доступных местах
        self.assertIn('available_rows', response.data)
        
        # В самолете 10 рядов, в одном билет уже занят, должно быть 10 рядов
        self.assertEqual(len(response.data['available_rows']), 10)
        
    def test_book_specific_seats(self):
        url = reverse('ticket-book-seats')
        data = {
            'flight_id': self.flight.id,
            'seats': [
                {'row': 2, 'seat': 2},
                {'row': 3, 'seat': 3}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Проверяем, что создано 2 новых билета
        self.assertEqual(Ticket.objects.count(), 3)  # 1 из setUp + 2 новых
        
        # Проверяем, что места забронированы правильно
        tickets = Ticket.objects.exclude(id=self.ticket.id)
        seats = [(t.row, t.seat) for t in tickets]
        self.assertIn((2, 2), seats)
        self.assertIn((3, 3), seats)
        
    def test_book_already_taken_seat(self):
        url = reverse('ticket-book-seats')
        data = {
            'flight_id': self.flight.id,
            'seats': [
                {'row': 1, 'seat': 1},  # Это место уже занято из setUp
                {'row': 2, 'seat': 2}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Проверяем, что новых билетов не создано
        self.assertEqual(Ticket.objects.count(), 1)

    def test_book_seats_with_string_format(self):
        """Тест бронирования мест с использованием строкового формата (для HTML-форм)"""
        url = reverse('ticket-book-seats')
        data = {
            'flight_id': self.flight.id,
            'rows': '2,3',
            'seat_numbers': '2,3'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Проверяем, что создано 2 новых билета
        self.assertEqual(Ticket.objects.count(), 3)  # 1 из setUp + 2 новых
        
        # Проверяем, что места забронированы правильно
        tickets = Ticket.objects.exclude(id=self.ticket.id)
        seats = [(t.row, t.seat) for t in tickets]
        self.assertIn((2, 2), seats)
        self.assertIn((3, 3), seats)

    def test_book_by_route(self):
        """Тест бронирования билетов через указание маршрута, а не конкретного рейса"""
        url = reverse('ticket-book-by-route')
        data = {
            'source': self.source_airport.id,
            'destination': self.destination_airport.id,
            'rows': '2,3',
            'seat_numbers': '2,3'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Проверяем, что создано 2 новых билета
        self.assertEqual(Ticket.objects.count(), 3)  # 1 из setUp + 2 новых
        
        # Проверяем, что билеты созданы для правильного рейса
        new_tickets = Ticket.objects.exclude(id=self.ticket.id)
        self.assertEqual(new_tickets.first().flight, self.flight)
        
        # Проверяем, что места забронированы правильно
        seats = [(t.row, t.seat) for t in new_tickets]
        self.assertIn((2, 2), seats)
        self.assertIn((3, 3), seats)
        
    def test_airports_list_in_ticket_list(self):
        """Тест получения списка аэропортов при запросе списка билетов"""
        url = reverse('ticket-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем, что в ответе есть список аэропортов
        self.assertIn('airports_list', response.data)
        self.assertEqual(len(response.data['airports_list']), 2)  # 2 аэропорта из setUp
