from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from airports.models import Airport
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
        help_text="ID of the departure airport",
    )
    destination_id = serializers.PrimaryKeyRelatedField(
        queryset=Airport.objects.all(),
        write_only=True,
        required=True,
        help_text="ID of the destination airport",
    )

    seat = serializers.IntegerField(
        min_value=1,
        required=False,
        write_only=True,
        help_text="Seat number (for a single seat)",
    )

    rows = serializers.CharField(
        required=False,
        write_only=True,
        help_text="Comma-separated list of rows, e.g., 1,2,3",
    )
    seat_numbers = serializers.CharField(
        required=False,
        write_only=True,
        help_text="Comma-separated list of seat numbers, e.g., 1,2,3",
    )

    tickets = serializers.ListField(read_only=True)

    class Meta:
        model = Ticket
        fields = [
            "id",
            "source_id",
            "destination_id",
            "seat",
            "rows",
            "seat_numbers",
            "tickets",
        ]
        read_only_fields = ["id", "tickets"]

    def validate(self, data):
        source = data.get("source_id")
        destination = data.get("destination_id")

        if source == destination:
            raise ValidationError("Source and destination airports cannot be the same")

        flight = (
            Flight.objects.filter(route__source=source, route__destination=destination)
            .order_by("departure_time")
            .first()
        )

        if not flight:
            raise ValidationError(
                f"No flight found from {source.name} to {destination.name}"
            )

        data["flight"] = flight

        has_seat = "seat" in data
        has_rows_seats = "rows" in data and "seat_numbers" in data

        if not has_seat and not has_rows_seats:
            raise ValidationError(
                "You must specify either seat or a combination of rows and seat_numbers"
            )

        if has_seat and has_rows_seats:
            raise ValidationError(
                "You can only specify one option: seat or rows+seat_numbers"
            )

        if has_rows_seats:
            try:
                rows = [
                    int(r.strip()) for r in data.pop("rows").split(",") if r.strip()
                ]
                seat_numbers = [
                    int(s.strip())
                    for s in data.pop("seat_numbers").split(",")
                    if s.strip()
                ]
            except ValueError:
                raise ValidationError(
                    "Rows and seat numbers must be integers separated by commas"
                )

            if len(rows) != len(seat_numbers):
                raise ValidationError(
                    "The number of rows must match the number of seat numbers"
                )

            data["rows_and_seats"] = list(zip(rows, seat_numbers))

        if has_seat:
            data["seats"] = [data.pop("seat")]

        return data

    def create(self, validated_data):
        request = self.context.get("request")
        flight = validated_data.get("flight")
        seats_requested = validated_data.get("seats", [])
        rows_and_seats = validated_data.get("rows_and_seats", [])

        order = Order.objects.create(user=request.user)

        tickets = []
        booked_seats = set(
            Ticket.objects.filter(flight=flight).values_list("row", "seat")
        )

        if rows_and_seats:
            for row, seat in rows_and_seats:
                if row < 1 or row > flight.airplane.rows:
                    order.delete()
                    raise ValidationError(
                        f"Row {row} does not exist on the airplane (total rows: {flight.airplane.rows})"
                    )

                if seat < 1 or seat > flight.airplane.seats_in_row:
                    order.delete()
                    raise ValidationError(
                        f"Seat {seat} does not exist in the row (total seats in row: {flight.airplane.seats_in_row})"
                    )

                if (row, seat) in booked_seats:
                    order.delete()
                    raise ValidationError(f"Seat {seat} in row {row} is already booked")

                ticket = Ticket.objects.create(
                    flight=flight, row=row, seat=seat, order=order
                )
                tickets.append(ticket)
                booked_seats.add((row, seat))

            return tickets

        all_seats = []
        for row in range(1, flight.airplane.rows + 1):
            for seat in range(1, flight.airplane.seats_in_row + 1):
                if (row, seat) not in booked_seats:
                    all_seats.append((row, seat))

        if len(all_seats) < len(seats_requested):
            order.delete()
            raise ValidationError(
                f"Not enough available seats. Available: {len(all_seats)}, requested: {len(seats_requested)}."
            )

        for requested_seat in seats_requested:
            available_row = None

            for row in range(1, flight.airplane.rows + 1):
                if (row, requested_seat) not in booked_seats:
                    available_row = row
                    break

            if available_row is None:
                if not all_seats:
                    order.delete()
                    raise ValidationError("No available seats")
                available_row, requested_seat = all_seats.pop(0)
            else:
                all_seats.remove((available_row, requested_seat))

            ticket = Ticket.objects.create(
                flight=flight, row=available_row, seat=requested_seat, order=order
            )
            tickets.append(ticket)
            booked_seats.add((available_row, requested_seat))

        return tickets


class FlightWithSeatsSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying a flight with available rows and seats
    """

    source = serializers.CharField(source="route.source.name", read_only=True)
    destination = serializers.CharField(source="route.destination.name", read_only=True)
    departure_date = serializers.DateTimeField(source="departure_time", read_only=True)
    available_seats = serializers.SerializerMethodField(read_only=True)
    available_rows = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Flight
        fields = [
            "id",
            "source",
            "destination",
            "departure_time",
            "arrival_time",
            "departure_date",
            "available_seats",
            "available_rows",
        ]

    def get_available_seats(self, obj):
        total_seats = obj.airplane.total_seats
        booked_seats = Ticket.objects.filter(flight=obj).count()
        return total_seats - booked_seats

    def get_available_rows(self, obj):
        # Get all booked seats
        booked_seats = set(Ticket.objects.filter(flight=obj).values_list("row", "seat"))

        # Create a dictionary of rows with available seats
        rows_with_seats = {}

        for row in range(1, obj.airplane.rows + 1):
            available_seats = []
            for seat in range(1, obj.airplane.seats_in_row + 1):
                if (row, seat) not in booked_seats:
                    available_seats.append(seat)

            if available_seats:  # Add the row only if it has available seats
                rows_with_seats[row] = available_seats

        # Format the result for usability
        result = []
        for row, seats in rows_with_seats.items():
            result.append({"row": row, "available_seats": seats})

        return result


class RouteBasedTicketBookingSerializer(serializers.Serializer):
    """
    Serializer for booking tickets based on a route instead of a specific flight
    """

    source = serializers.PrimaryKeyRelatedField(queryset=Airport.objects.all())
    destination = serializers.PrimaryKeyRelatedField(queryset=Airport.objects.all())

    # Fields for HTML form support (preferred for frontend input)
    rows = serializers.CharField(
        required=False,
        help_text="Comma-separated list of rows, e.g., 1,2,3",
        write_only=True,
    )
    seat_numbers = serializers.CharField(
        required=False,
        help_text="Comma-separated list of seats, e.g., 1,2,3",
        write_only=True,
    )

    def validate(self, data):
        # Ensure source and destination are not the same
        if data.get("source") == data.get("destination"):
            raise serializers.ValidationError(
                "Departure and arrival airports must differ"
            )

        # Look for a matching flight
        flight = (
            Flight.objects.filter(
                route__source=data.get("source"),
                route__destination=data.get("destination"),
                # Additional filters like time can be added here
                # departure_time__gt=timezone.now()
            )
            .order_by("departure_time")
            .first()
        )

        if not flight:
            raise serializers.ValidationError(
                "No matching flights found for the given route"
            )

        # Store the found flight in validated_data
        data["flight"] = flight

        # Ensure at least one seat option is specified: either 'seats' or 'rows' + 'seat_numbers'
        if "seats" not in data and ("rows" not in data or "seat_numbers" not in data):
            raise serializers.ValidationError(
                "You must provide either a 'seats' list or both 'rows' and 'seat_numbers'"
            )

        # If 'rows' and 'seat_numbers' are provided, convert them to the 'seats' format
        if "rows" in data and "seat_numbers" in data:
            rows = [int(x.strip()) for x in data["rows"].split(",") if x.strip()]
            seat_numbers = [
                int(x.strip()) for x in data["seat_numbers"].split(",") if x.strip()
            ]

            # Ensure the number of rows and seats matches
            if len(rows) != len(seat_numbers):
                raise serializers.ValidationError(
                    "The number of rows and seat numbers must match"
                )

            # Create the 'seats' array
            data["seats"] = [
                {"row": row, "seat": seat} for row, seat in zip(rows, seat_numbers)
            ]

        # Validate that requested seats exist and are not booked
        available_rows = range(1, flight.airplane.rows + 1)
        available_seats_in_row = range(1, flight.airplane.seats_in_row + 1)

        # Get already booked seats
        booked_seats = list(
            Ticket.objects.filter(flight=flight).values_list("row", "seat")
        )

        for seat_data in data["seats"]:
            row = seat_data["row"]
            seat = seat_data["seat"]

            # Check if the row and seat exist
            if row not in available_rows:
                raise serializers.ValidationError(
                    f"Row {row} does not exist on the airplane"
                )
            if seat not in available_seats_in_row:
                raise serializers.ValidationError(
                    f"Seat {seat} does not exist in row {row}"
                )

            # Check if the seat is already booked
            if (row, seat) in booked_seats:
                raise serializers.ValidationError(
                    f"Seat {row}-{seat} is already booked"
                )

        return data

    def create(self, validated_data):
        flight = validated_data["flight"]
        seats_data = validated_data["seats"]

        # Create an order if one doesn't already exist
        user = self.context["request"].user
        order = Order.objects.create(user=user)

        # Create tickets
        tickets = []
        for seat_data in seats_data:
            ticket = Ticket.objects.create(
                flight=flight, order=order, row=seat_data["row"], seat=seat_data["seat"]
            )
            tickets.append(ticket)

        return tickets
