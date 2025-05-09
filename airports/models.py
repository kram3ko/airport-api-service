from django.db import models
from django.core.validators import MinValueValidator


class Airport(models.Model):
    """
    Model representing an airport with location information.
    """

    name = models.CharField(max_length=100, unique=True, db_index=True)
    city = models.CharField(max_length=100, db_index=True)
    country = models.CharField(max_length=100, db_index=True)
    closest_big_city = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Airport"
        verbose_name_plural = "Airports"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "city", "country"],
                name="unique_airport_name_city_country",
            )
        ]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["city"]),
            models.Index(fields=["country"]),
        ]

    def __str__(self):
        return f"{self.name} - {self.city}, {self.country}"


class Route(models.Model):
    """
    Model representing a flight route between two airports.
    """

    source = models.ForeignKey(
        to=Airport, on_delete=models.CASCADE, related_name="source_routes"
    )
    destination = models.ForeignKey(
        to=Airport, on_delete=models.CASCADE, related_name="destination_routes"
    )
    distance = models.PositiveIntegerField(
        validators=[MinValueValidator(1, message="Distance must be greater than 0")]
    )
    flight_number = models.CharField(max_length=50, db_index=True)

    class Meta:
        ordering = ["flight_number"]
        verbose_name = "Route"
        verbose_name_plural = "Routes"
        constraints = [
            models.UniqueConstraint(
                fields=["source", "destination", "flight_number"], name="unique_route"
            )
        ]
        indexes = [
            models.Index(fields=["flight_number"]),
        ]

    def __str__(self):
        return f"{self.source} - {self.destination} ({self.flight_number})"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.source == self.destination:
            raise ValidationError("Source and destination airports cannot be the same.")
