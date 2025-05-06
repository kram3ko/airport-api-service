from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
import datetime

from base.mixins import BaseViewSetMixin
from base.pagination import DefaultPagination
from tickets.models import Order, Ticket
from flights.models import Flight
from tickets.serializers import (
    OrderSerializer,
    TicketSerializer,
    TicketListSerializer,
    OrderListSerializer,
    TicketCreateSerializer,
    TickerDetailSerializer,
    OrderCreateSerializer,
    FlightWithSeatsSerializer,
    TicketBookingSerializer,
    RouteBasedTicketBookingSerializer
)
from airports.models import Airport


class OrderViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user']
    search_fields = ['id']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    action_serializers = {
        "list": OrderListSerializer,
        "create": OrderCreateSerializer,
    }

    def get_queryset(self):
        # Only show current user's orders
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)


class TicketViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['flight', 'order', 'flight__route__source', 'flight__route__destination']
    search_fields = ['flight__route__source__name', 'flight__route__destination__name']
    ordering_fields = ['flight__departure_time']
    ordering = ['flight__departure_time']

    action_serializers = {
        "list": TicketListSerializer,
        "create": TicketCreateSerializer,
        "retrieve": TickerDetailSerializer,
        "update": TicketCreateSerializer,
        "flight_seats": FlightWithSeatsSerializer,
        "book_seats": TicketBookingSerializer,
        "book_by_route": RouteBasedTicketBookingSerializer,
    }

    def get_queryset(self):
        # Only show current user's tickets unless staff
        user = self.request.user
        if user.is_staff:
            return Ticket.objects.all()
        return Ticket.objects.filter(order__user=user)

    @action(detail=False, methods=["get"])
    def booking_info(self, request):
        """
        Получить информацию, необходимую для создания билета:
        - список аэропортов
        - список маршрутов
        - список ближайших рейсов
        """
        # Добавляем к response список всех аэропортов для формы создания билетов
        airports = Airport.objects.all()
        airport_data = [{'id': a.id, 'name': str(a)} for a in airports]

        # Получаем список доступных маршрутов
        routes_data = []
        for route in Flight.objects.values('route__source', 'route__destination', 'route__source__name',
                                           'route__destination__name').distinct():
            routes_data.append({
                'source_id': route['route__source'],
                'destination_id': route['route__destination'],
                'source_name': route['route__source__name'],
                'destination_name': route['route__destination__name'],
            })

        # Добавляем список рейсов на ближайшее время
        upcoming_flights = Flight.objects.filter(
            departure_time__gte=timezone.now()
        ).order_by('departure_time')[:10]  # Ограничиваем 10 ближайшими рейсами

        upcoming_flights_data = []
        for flight in upcoming_flights:
            # Получаем информацию о свободных местах
            total_seats = flight.airplane.total_seats
            booked_seats_count = Ticket.objects.filter(flight=flight).count()
            available_seats_count = total_seats - booked_seats_count

            upcoming_flights_data.append({
                'id': flight.id,
                'source': flight.route.source.name,
                'destination': flight.route.destination.name,
                'departure_time': flight.departure_time,
                'arrival_time': flight.arrival_time,
                'available_seats': available_seats_count
            })

        # Формируем ответ с информацией для создания билета
        return Response({
            'airports_list': airport_data,
            'routes_list': routes_data,
            'upcoming_flights': upcoming_flights_data
        })

    @action(detail=True, methods=["get"])
    def flight_seats(self, request, pk=None):
        """Получение информации о доступных местах на конкретном рейсе"""
        try:
            flight = Flight.objects.get(pk=pk)
        except Flight.DoesNotExist:
            return Response(
                {"detail": "Рейс не найден"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = FlightWithSeatsSerializer(flight)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def book_seats(self, request):
        """
        Бронирование билетов с указанием конкретных рядов и мест
        
        Поддерживает два формата данных:
        
        1. JSON формат (для API):
        {
            "flight_id": 1,
            "seats": [
                {"row": 1, "seat": 2},
                {"row": 1, "seat": 3}
            ]
        }
        
        2. Формат для HTML-форм:
        flight_id=1&rows=1,1&seat_numbers=2,3
        
        где rows - список рядов через запятую,
        seat_numbers - список номеров мест через запятую
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tickets = serializer.save()

        return Response(
            {"tickets": TicketListSerializer(tickets, many=True).data},
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=["post"])
    def book_by_route(self, request):
        """
        Бронирование билетов с указанием маршрута (откуда/куда)
        
        Формат данных для HTML-форм:
        - source: ID аэропорта отправления (обязательно)
        - destination: ID аэропорта прибытия (обязательно)
        - rows: Список рядов через запятую, например: "1,2,3"
        - seat_numbers: Список мест через запятую, например: "1,2,3"
        
        Например:
        source=1&destination=2&rows=1,2&seat_numbers=3,4
        
        Система сама найдет подходящий рейс по указанному маршруту.
        Не используйте поле seats в HTML-формах - оно предназначено только для API запросов.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tickets = serializer.save()

        return Response(
            {"tickets": TicketListSerializer(tickets, many=True).data},
            status=status.HTTP_201_CREATED
        )

