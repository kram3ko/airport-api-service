# Register your models here.

from django.contrib import admin
from tickets.models import Order, Ticket


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 0
    autocomplete_fields = ["flight"]
    readonly_fields = ["created_at"]

    def created_at(self, obj):
        return obj.order.created_at

    created_at.short_description = "Ordered at"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at", "get_ticket_count")
    list_filter = ("created_at", "user")
    search_fields = ("user__username", "user__email")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at",)
    inlines = [TicketInline]

    def get_ticket_count(self, obj):
        return obj.tickets.count()

    get_ticket_count.short_description = "Tickets"


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "flight", "row", "seat", "get_user", "get_created_at")
    list_filter = (
        "flight__route__source",
        "flight__route__destination",
        "order__created_at",
    )
    search_fields = (
        "flight__route__source__name",
        "flight__route__destination__name",
        "order__user__username",
        "order__user__email",
    )
    autocomplete_fields = ["flight", "order"]
    readonly_fields = ("get_created_at",)

    def get_user(self, obj):
        return obj.order.user

    get_user.short_description = "User"
    get_user.admin_order_field = "order__user"

    def get_created_at(self, obj):
        return obj.order.created_at

    get_created_at.short_description = "Ordered at"
    get_created_at.admin_order_field = "order__created_at"
