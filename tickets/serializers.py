from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from airports.models import Airport
from airports.serializers import RouteCreateSerializer
from flights.models import Flight
from flights.serializers import FlightSerializer, FlightListSerializer
from tickets.models import Ticket, Order
from users.serializers import UserSerializer


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "created_at", "user"]
        read_only_fields = ["id", "created_at"]


class TicketSerializer(serializers.ModelSerializer):
    flight = FlightSerializer(many=False, read_only=True)

    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "flight", "order"]


class OrderListSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    tickets = TicketSerializer(many=True, read_only=True)
    flight = FlightListSerializer(many=False, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "created_at", "user", "tickets", "flight"]
        read_only_fields = ["id", "created_at", "user"]


class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "user"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["user"] = request.user
        return super().create(validated_data)


class TicketListSerializer(serializers.ModelSerializer):
    order = OrderSerializer(many=False, read_only=True)
    flight = FlightListSerializer(many=False, read_only=True)

    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "flight", "order"]
        read_only_fields = ["id", "order"]


class TickerDetailSerializer(serializers.ModelSerializer):
    flight = FlightListSerializer(many=False, read_only=True)
    order = OrderSerializer(many=False, read_only=True)
    airstrip = serializers.CharField(source="flight.route.source", read_only=True)

    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "flight", "order", "airstrip"]
        read_only_fields = ["id", "order"]


class TicketCreateSerializer(serializers.ModelSerializer):
    source_id = serializers.PrimaryKeyRelatedField(
        queryset=Airport.objects.all(),
        write_only=True,
        required=True,
        help_text="ID аэропорта отправления"
    )
    destination_id = serializers.PrimaryKeyRelatedField(
        queryset=Airport.objects.all(),
        write_only=True,
        required=True,
        help_text="ID аэропорта назначения"
    )

    seat = serializers.IntegerField(
        min_value=1,
        required=False,
        write_only=True,
        help_text="Номер места (для одного места)"
    )

    # Поля для HTML-форм (предпочтительный способ)
    rows = serializers.CharField(
        required=False,
        write_only=True,
        help_text="Список рядов через запятую, например: 1,2,3"
    )
    seat_numbers = serializers.CharField(
        required=False,
        write_only=True,
        help_text="Список мест через запятую, например: 1,2,3"
    )

    tickets = serializers.ListField(read_only=True)

    class Meta:
        model = Ticket
        fields = [
            "id", "source_id", "destination_id",
            "seat", "rows", "seat_numbers", "tickets"
        ]
        read_only_fields = ["id", "tickets"]

    def validate(self, data):
        # Получаем аэропорты
        source = data.get('source_id')
        destination = data.get('destination_id')

        # Проверяем, что пункты отправления и назначения не совпадают
        if source == destination:
            raise ValidationError("Пункты отправления и назначения не могут совпадать")

        # Находим подходящий рейс
        flight = Flight.objects.filter(
            route__source=source,
            route__destination=destination
        ).order_by('departure_time').first()

        if not flight:
            raise ValidationError(f"Не найден рейс из {source.name} в {destination.name}")

        # Сохраняем найденный рейс
        data['flight'] = flight

        # Проверяем, что указан хотя бы один из способов выбора мест
        has_seat = 'seat' in data
        has_seats = 'seats' in data
        has_rows_seats = 'rows' in data and 'seat_numbers' in data

        if not has_seat and not has_seats and not has_rows_seats:
            raise ValidationError("Необходимо указать seat, seats или комбинацию rows и seat_numbers")

        # Убеждаемся, что не указано более одного способа выбора мест
        if (has_seat and has_seats) or (has_seat and has_rows_seats) or (has_seats and has_rows_seats):
            raise ValidationError("Можно указать только один из вариантов: seat, seats или rows+seat_numbers")

        # Если указаны rows и seat_numbers, преобразуем их в список seats
        if has_rows_seats:
            try:
                rows = [int(r.strip()) for r in data.pop('rows').split(',') if r.strip()]
                seat_numbers = [int(s.strip()) for s in data.pop('seat_numbers').split(',') if s.strip()]
            except ValueError:
                raise ValidationError("Ряды и места должны быть целыми числами, разделенными запятыми")

            if len(rows) != len(seat_numbers):
                raise ValidationError("Количество рядов должно совпадать с количеством мест")

            # Создаем специальный формат для дальнейшей обработки
            data['rows_and_seats'] = list(zip(rows, seat_numbers))

        # Если указан одиночный seat, преобразуем его в список seats
        if has_seat:
            data['seats'] = [data.pop('seat')]

        return data

    def create(self, validated_data):
        request = self.context.get("request")
        flight = validated_data.get('flight')
        seats_requested = validated_data.get('seats', [])
        rows_and_seats = validated_data.get('rows_and_seats', [])

        # Создаем новый заказ для текущего пользователя
        order = Order.objects.create(user=request.user)

        tickets = []
        # Получаем все занятые места для рейса
        booked_seats = set(Ticket.objects.filter(flight=flight).values_list('row', 'seat'))

        # Если указаны конкретные ряды и места
        if rows_and_seats:
            for row, seat in rows_and_seats:
                # Проверяем, что место существует в самолете
                if row < 1 or row > flight.airplane.rows:
                    order.delete()
                    raise ValidationError(f"Ряд {row} не существует в самолете (всего рядов: {flight.airplane.rows})")

                if seat < 1 or seat > flight.airplane.seats_in_row:
                    order.delete()
                    raise ValidationError(
                        f"Место {seat} не существует в ряду (всего мест в ряду: {flight.airplane.seats_in_row})"
                    )

                # Проверяем, что место не занято
                if (row, seat) in booked_seats:
                    order.delete()
                    raise ValidationError(f"Место {seat} в ряду {row} уже занято")

                # Создаем билет
                ticket = Ticket.objects.create(
                    flight=flight,
                    row=row,
                    seat=seat,
                    order=order
                )
                tickets.append(ticket)
                booked_seats.add((row, seat))

            return tickets

        # Если указаны только номера мест (без рядов)
        # Создаем список всех возможных мест в самолете
        all_seats = []
        for row in range(1, flight.airplane.rows + 1):
            for seat in range(1, flight.airplane.seats_in_row + 1):
                if (row, seat) not in booked_seats:
                    all_seats.append((row, seat))

        # Если свободных мест меньше, чем запрошено
        if len(all_seats) < len(seats_requested):
            order.delete()
            raise ValidationError(
                f"Недостаточно свободных мест. Доступно {len(all_seats)}, запрошено {len(seats_requested)}.")

        # Для каждого запрошенного места пытаемся найти свободное
        for requested_seat in seats_requested:
            # Пытаемся найти место с таким номером в любом доступном ряду
            available_row = None

            # Проверяем все ряды на наличие свободного места с указанным номером
            for row in range(1, flight.airplane.rows + 1):
                if (row, requested_seat) not in booked_seats:
                    available_row = row
                    break

            # Если не нашли подходящее место в другом ряду, берем первое свободное
            if available_row is None:
                if not all_seats:
                    order.delete()
                    raise ValidationError("Нет свободных мест")
                available_row, requested_seat = all_seats.pop(0)
            else:
                # Удаляем найденное место из списка доступных
                all_seats.remove((available_row, requested_seat))

            # Создаем билет на найденное место
            ticket = Ticket.objects.create(
                flight=flight,
                row=available_row,
                seat=requested_seat,
                order=order
            )
            tickets.append(ticket)

            # Обновляем список занятых мест
            booked_seats.add((available_row, requested_seat))

        return tickets


class FlightWithSeatsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения рейса с доступными рядами и местами
    """
    source = serializers.CharField(source='route.source.name', read_only=True)
    destination = serializers.CharField(source='route.destination.name', read_only=True)
    departure_date = serializers.DateTimeField(source='departure_time', read_only=True)
    available_seats = serializers.SerializerMethodField(read_only=True)
    available_rows = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Flight
        fields = ['id', 'source', 'destination', 'departure_time', 'arrival_time',
                  'departure_date', 'available_seats', 'available_rows']

    def get_available_seats(self, obj):
        total_seats = obj.airplane.total_seats
        booked_seats = Ticket.objects.filter(flight=obj).count()
        return total_seats - booked_seats

    def get_available_rows(self, obj):
        # Получаем все занятые места
        booked_seats = set(Ticket.objects.filter(flight=obj).values_list('row', 'seat'))

        # Создаем словарь рядов с доступными местами
        rows_with_seats = {}

        for row in range(1, obj.airplane.rows + 1):
            available_seats = []
            for seat in range(1, obj.airplane.seats_in_row + 1):
                if (row, seat) not in booked_seats:
                    available_seats.append(seat)

            if available_seats:  # Добавляем ряд только если есть доступные места
                rows_with_seats[row] = available_seats

        # Форматируем результат для удобства использования
        result = []
        for row, seats in rows_with_seats.items():
            result.append({
                'row': row,
                'available_seats': seats
            })

        return result


class TicketBookingSerializer(serializers.Serializer):
    """
    Сериализатор для бронирования билетов с указанием рядов и мест
    """
    flight_id = serializers.PrimaryKeyRelatedField(queryset=Flight.objects.all())

    # Поддержка JSON-формата для API
    seats = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField(),
            allow_empty=False
        ),
        min_length=1,
        required=False
    )

    # Поддержка формата HTML-форм
    rows = serializers.CharField(required=False, help_text="Список рядов через запятую, например: 1,2,3")
    seat_numbers = serializers.CharField(required=False, help_text="Список мест через запятую, например: 1,2,3")

    def validate(self, data):
        # Проверяем, что указан либо seats, либо пара rows/seat_numbers
        has_seats = 'seats' in data and data['seats']
        has_rows_seats = 'rows' in data and data['rows'] and 'seat_numbers' in data and data['seat_numbers']

        if not has_seats and not has_rows_seats:
            raise ValidationError("Необходимо указать либо seats, либо пару rows/seat_numbers")

        if has_seats and has_rows_seats:
            raise ValidationError("Можно указать либо seats, либо пару rows/seat_numbers, но не оба варианта")

        # Если указаны rows и seat_numbers, преобразуем их в формат seats
        if has_rows_seats:
            rows = [int(r.strip()) for r in data['rows'].split(',') if r.strip()]
            seat_numbers = [int(s.strip()) for s in data['seat_numbers'].split(',') if s.strip()]

            if len(rows) != len(seat_numbers):
                raise ValidationError("Количество рядов должно совпадать с количеством мест")

            seats = [{'row': r, 'seat': s} for r, s in zip(rows, seat_numbers)]
            data['seats'] = seats

            # Удаляем исходные поля, чтобы не путались
            del data['rows']
            del data['seat_numbers']

        flight = data.get('flight_id')
        seats_data = data.get('seats')

        # Получаем все занятые места
        booked_seats = set(Ticket.objects.filter(flight=flight).values_list('row', 'seat'))

        # Проверяем, что все выбранные места свободны и существуют
        for seat_item in seats_data:
            row = seat_item['row']
            seat = seat_item['seat']

            # Проверяем, что ряд и место существуют в самолете
            if row < 1 or row > flight.airplane.rows:
                raise ValidationError(f"Ряд {row} не существует в самолете (всего рядов: {flight.airplane.rows})")

            if seat < 1 or seat > flight.airplane.seats_in_row:
                raise ValidationError(
                    f"Место {seat} не существует в ряду (всего мест в ряду: {flight.airplane.seats_in_row})"
                )

            # Проверяем, что место не занято
            if (row, seat) in booked_seats:
                raise ValidationError(f"Место {seat} в ряду {row} уже занято")

        return data

    def create(self, validated_data):
        flight = validated_data.get('flight_id')
        seats_data = validated_data.get('seats')
        request = self.context.get('request')

        # Создаем заказ
        order = Order.objects.create(user=request.user)

        # Создаем билеты
        tickets = []
        for seat_item in seats_data:
            ticket = Ticket.objects.create(
                flight=flight,
                row=seat_item['row'],
                seat=seat_item['seat'],
                order=order
            )
            tickets.append(ticket)

        return tickets


class RouteBasedTicketBookingSerializer(serializers.Serializer):
    """Сериализатор для создания билетов по маршруту вместо конкретного рейса"""
    source = serializers.PrimaryKeyRelatedField(queryset=Airport.objects.all())
    destination = serializers.PrimaryKeyRelatedField(queryset=Airport.objects.all())

    # Поля для поддержки ввода через HTML-форму (предпочтительно использовать эти поля)
    rows = serializers.CharField(
        required=False,
        help_text="Список рядов через запятую, например: 1,2,3",
        write_only=True
    )
    seat_numbers = serializers.CharField(
        required=False,
        help_text="Список мест через запятую, например: 1,2,3",
        write_only=True
    )

    # Поле для поддержки JSON формата (только для API запросов, не для HTML-форм)
    seats = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        write_only=True,
        help_text="Не использовать в HTML-формах! Только для API запросов.",
        style={'display': 'none'}  # Скрываем из HTML-формы
    )

    def validate(self, data):
        # Проверяем, что source и destination не совпадают
        if data.get('source') == data.get('destination'):
            raise serializers.ValidationError("Аэропорты отправления и прибытия не могут совпадать")

        # Ищем подходящий рейс
        flight = Flight.objects.filter(
            route__source=data.get('source'),
            route__destination=data.get('destination'),
            # Можно добавить дополнительные фильтры, например, по времени
            # departure_time__gt=timezone.now()
        ).order_by('departure_time').first()

        if not flight:
            raise serializers.ValidationError("Не найдено подходящих рейсов для указанного маршрута")

        # Сохраняем найденный рейс в validated_data
        data['flight'] = flight

        # Проверяем, что указан хотя бы один из вариантов: seats или rows+seat_numbers
        if 'seats' not in data and ('rows' not in data or 'seat_numbers' not in data):
            raise serializers.ValidationError("Необходимо указать либо массив seats, либо строки rows и seat_numbers")

        # Если указаны rows и seat_numbers, преобразуем их в формат seats
        if 'rows' in data and 'seat_numbers' in data:
            rows = [int(x.strip()) for x in data['rows'].split(',') if x.strip()]
            seat_numbers = [int(x.strip()) for x in data['seat_numbers'].split(',') if x.strip()]

            # Проверяем, что количество рядов и мест совпадает
            if len(rows) != len(seat_numbers):
                raise serializers.ValidationError("Количество рядов и мест должно совпадать")

            # Создаем массив seats
            data['seats'] = [{'row': row, 'seat': seat} for row, seat in zip(rows, seat_numbers)]

        # Проверяем, что все запрошенные места существуют и не заняты
        available_rows = range(1, flight.airplane.rows + 1)
        available_seats_in_row = range(1, flight.airplane.seats_in_row + 1)

        # Получаем уже занятые места
        booked_seats = list(Ticket.objects.filter(flight=flight).values_list('row', 'seat'))

        for seat_data in data['seats']:
            row = seat_data['row']
            seat = seat_data['seat']

            # Проверка, что ряд и место существуют
            if row not in available_rows:
                raise serializers.ValidationError(f"Ряд {row} не существует в самолете")
            if seat not in available_seats_in_row:
                raise serializers.ValidationError(f"Место {seat} не существует в ряду")

            # Проверка, что место не занято
            if (row, seat) in booked_seats:
                raise serializers.ValidationError(f"Место {row}-{seat} уже занято")

        return data

    def create(self, validated_data):
        flight = validated_data['flight']
        seats_data = validated_data['seats']

        # Создаем заказ, если он не был предоставлен
        user = self.context['request'].user
        order = Order.objects.create(user=user)

        # Создаем билеты
        tickets = []
        for seat_data in seats_data:
            ticket = Ticket.objects.create(
                flight=flight,
                order=order,
                row=seat_data['row'],
                seat=seat_data['seat']
            )
            tickets.append(ticket)

        return tickets

    def to_representation(self, instance):
        # Этот метод вызывается при сериализации объекта в JSON
        if isinstance(instance, list):
            # Если возвращается список билетов, сериализуем каждый
            return {
                'tickets': TicketListSerializer(instance, many=True).data
            }
        # Иначе возвращаем стандартную сериализацию
        return super().to_representation(instance)
