from django.contrib.auth import get_user_model
from django.db import models

from flights.models import Flight

User = get_user_model()


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")

    def __str__(self):
        return f"Order {self.id} by {self.user.email}"


class Ticket(models.Model):
    row = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["flight", "row", "seat"], name="unique_flight_row_seat"
            )
        ]

    def __str__(self):
        return (
            f"Ticket {self.id} for Flight {self.flight}"
            f" (Row: {self.row}, Seat: {self.seat})"
        )
