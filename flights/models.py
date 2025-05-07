from django.db import models
from airports.models import Route
from airplanes.models import Airplane


class Crew(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    rang = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Flight(models.Model):
    route = models.ForeignKey(to=Route, on_delete=models.CASCADE, related_name="routes")
    airplane = models.ForeignKey(
        to=Airplane, on_delete=models.CASCADE, related_name="airplanes"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, related_name="flights")

    def __str__(self):
        return f"Flight from {self.route.source} to {self.route.destination} by airplane {self.airplane.name}"
