from django.db import models


class AirplaneType(models.Model):
    name = models.CharField(max_length=100)


class Airplane(models.Model):
    name = models.CharField(max_length=100)
    rows = models.PositiveIntegerField()
    seats_in_row = models.PositiveIntegerField()
    airplane_type = models.ForeignKey(
        to=AirplaneType,
        on_delete=models.CASCADE,
        related_name="airplanes"
    )
