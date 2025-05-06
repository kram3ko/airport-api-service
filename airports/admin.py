# Register your models here.

from django.contrib import admin
from airports.models import Airport, Route


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "country", "closest_big_city")
    list_filter = ("country", "city")
    search_fields = ("name", "city", "country")
    ordering = ("name", "country", "city")


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("flight_number", "source", "destination", "distance")
    list_filter = ("source__country", "destination__country")
    search_fields = ("flight_number", "source__name", "destination__name")
    autocomplete_fields = ("source", "destination")
    ordering = ("flight_number",)
