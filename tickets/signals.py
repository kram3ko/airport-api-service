from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from tickets.models import Order, Ticket


@receiver([post_save, post_delete], sender=Order)
def order_list_cache_invalidation(*args, **kwargs):
    cache.delete_pattern("*order-list*")


@receiver([post_save, post_delete], sender=Ticket)
def book_by_route_cache_invalidation(*args, **kwargs):
    cache.delete_pattern("*ticket-list*")
