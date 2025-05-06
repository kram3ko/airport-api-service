from django.db import models


class Airport(models.Model):
    name = models.CharField(max_length=100, unique=True)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    closest_big_city = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "city", "country"],
                name="unique_airport_name_city_country",
            )
        ]
    def __str__(self):
        return f"{self.name} - {self.city}, {self.country}"

class Route(models.Model):
    source = models.ForeignKey(
        to=Airport, on_delete=models.CASCADE, related_name="source_airport"
    )
    destination = models.ForeignKey(
        to=Airport, on_delete=models.CASCADE, related_name="destination_airport"
    )
    distance = models.PositiveIntegerField()
    flight_number = models.CharField(max_length=50)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["source", "destination", "flight_number"], name="unique_route"
            )
        ]

    def __str__(self):
        return f"{self.source} - {self.destination} ({self.flight_number})"