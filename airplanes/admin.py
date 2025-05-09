# Register your models here.

from django.contrib import admin

from .models import Airplane, AirplaneType


@admin.register(AirplaneType)
class AirplaneTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category")
    list_filter = ("category",)
    search_fields = ("name", "category")


@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "rows",
        "seats_in_row",
        "airplane_type",
        "total_seats",
    )
    list_filter = ("airplane_type__category",)
    search_fields = ("name", "airplane_type__name")
    autocomplete_fields = ("airplane_type",)
    readonly_fields = ("total_seats",)
