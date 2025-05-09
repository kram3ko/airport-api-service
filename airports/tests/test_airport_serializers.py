from rest_framework.test import APITestCase
from airports.models import Airport, Route
from airports.serializers import (
    AirportSerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteCreateSerializer,
    RouteUpdateSerializer,
)


class AirportSerializerTest(APITestCase):
    def test_airport_serializer(self):
        airport = Airport.objects.create(
            name="Heathrow", city="London", country="UK", closest_big_city="London"
        )
        serializer = AirportSerializer(airport)
        self.assertEqual(serializer.data["name"], "Heathrow")
        self.assertEqual(serializer.data["city"], "London")


class RouteSerializerTest(APITestCase):
    def test_route_serializer(self):
        source = Airport.objects.create(name="JFK", city="New York", country="USA")
        destination = Airport.objects.create(name="LAX", city="Los Angeles", country="USA")
        route = Route.objects.create(
            source=source, destination=destination, distance=4000, flight_number="AA100"
        )
        serializer = RouteSerializer(route)
        self.assertEqual(serializer.data["source"]["name"], "JFK")
        self.assertEqual(serializer.data["destination"]["name"], "LAX")


class RouteListSerializerTest(APITestCase):
    def test_route_list_serializer(self):
        source = Airport.objects.create(name="JFK", city="New York", country="USA")
        destination = Airport.objects.create(name="LAX", city="Los Angeles", country="USA")
        route = Route.objects.create(
            source=source, destination=destination, distance=4000, flight_number="AA100"
        )
        serializer = RouteListSerializer(route)
        self.assertEqual(serializer.data["distance"], 4000)
        self.assertEqual(serializer.data["flight_number"], "AA100")


class RouteCreateSerializerTest(APITestCase):
    def test_route_create_serializer(self):
        source = Airport.objects.create(name="JFK", city="New York", country="USA")
        destination = Airport.objects.create(name="LAX", city="Los Angeles", country="USA")
        data = {
            "source": source.id,
            "destination": destination.id,
            "distance": 4000,
            "flight_number": "AA100",
        }
        serializer = RouteCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        route = serializer.save()
        self.assertEqual(route.source, source)
        self.assertEqual(route.destination, destination)


class RouteUpdateSerializerTest(APITestCase):
    def test_route_update_serializer(self):
        source = Airport.objects.create(name="JFK", city="New York", country="USA")
        destination = Airport.objects.create(name="LAX", city="Los Angeles", country="USA")
        route = Route.objects.create(
            source=source, destination=destination, distance=4000, flight_number="AA100"
        )
        new_destination = Airport.objects.create(name="ORD", city="Chicago", country="USA")
        data = {"destination": new_destination.id}
        serializer = RouteUpdateSerializer(route, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_route = serializer.save()
        self.assertEqual(updated_route.destination, new_destination)