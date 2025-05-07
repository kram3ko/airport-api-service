from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth import get_user_model

from airports.models import Airport, Route

User = get_user_model()


class AirportModelTests(TestCase):
    def setUp(self):
        self.airport = Airport.objects.create(
            name="Test Airport", city="Test City", country="Test Country"
        )

    def test_airport_creation(self):
        self.assertEqual(self.airport.name, "Test Airport")
        self.assertEqual(self.airport.city, "Test City")
        self.assertEqual(self.airport.country, "Test Country")

    def test_airport_str_representation(self):
        self.assertEqual(str(self.airport), "Test Airport - Test City, Test Country")

    def test_name_capitalization(self):
        airport = Airport.objects.create(
            name="lower airport", city="lower city", country="lower country"
        )
        self.assertEqual(airport.name, "Lower Airport")
        self.assertEqual(airport.city, "Lower City")
        self.assertEqual(airport.country, "Lower Country")

    def test_unique_constraint(self):
        with self.assertRaises(IntegrityError):
            Airport.objects.create(
                name="Test Airport", city="Test City", country="Test Country"
            )


class RouteModelTests(TestCase):
    def setUp(self):
        self.airport1 = Airport.objects.create(
            name="First Airport", city="First City", country="First Country"
        )
        self.airport2 = Airport.objects.create(
            name="Second Airport", city="Second City", country="Second Country"
        )
        self.route = Route.objects.create(
            source=self.airport1,
            destination=self.airport2,
            distance=1000,
            flight_number="TEST123",
        )

    def test_route_creation(self):
        self.assertEqual(self.route.source, self.airport1)
        self.assertEqual(self.route.destination, self.airport2)
        self.assertEqual(self.route.distance, 1000)
        self.assertEqual(self.route.flight_number, "TEST123")

    def test_route_str_representation(self):
        expected = f"{self.airport1} - {self.airport2} (TEST123)"
        self.assertEqual(str(self.route), expected)

    def test_different_source_destination_constraint(self):
        with self.assertRaises(ValidationError):
            route = Route(
                source=self.airport1,
                destination=self.airport1,
                distance=500,
                flight_number="TEST456",
            )
            route.clean()

    def test_unique_route_constraint(self):
        with self.assertRaises(IntegrityError):
            Route.objects.create(
                source=self.airport1,
                destination=self.airport2,
                distance=1500,
                flight_number="TEST123",
            )
