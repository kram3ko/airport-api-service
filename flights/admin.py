from django.contrib import admin

from .models import Crew, Flight


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ("id", "route", "airplane", "departure_time", "arrival_time")
    list_filter = ("route__source", "route__destination", "departure_time")
    search_fields = (
        "id",
        "route__source__name",
        "route__destination__name",
        "route__flight_number",
    )
    autocomplete_fields = ("route", "airplane")
    filter_horizontal = ("crew",)
    date_hierarchy = "departure_time"


@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "rang")
    list_filter = ("rang",)
    search_fields = ("first_name", "last_name")
