from django.db import models
from django_resized import ResizedImageField


class AirplaneType(models.Model):
    class AirplaneCategory(models.TextChoices):
        PASSENGER = "Passenger", "Passenger"
        PRIVATE = "Private", "Private"
        CARGO = "Cargo", "Cargo"

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(
        max_length=20, choices=AirplaneCategory.choices, null=True, blank=True
    )

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.name} - cat: {self.category}"


class Airplane(models.Model):
    name = models.CharField(max_length=100, unique=True)
    rows = models.PositiveIntegerField()
    seats_in_row = models.PositiveIntegerField()
    airplane_type = models.ForeignKey(
        to=AirplaneType, on_delete=models.CASCADE, related_name="airplanes"
    )
    photo = ResizedImageField(
        size=[300, 300],
        upload_to="airplanes/",
        force_format="JPEG",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["id"]

    @property
    def total_seats(self):
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name
