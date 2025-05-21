# signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Order, WaterProduct

@receiver(post_save, sender=Order)
def update_stock_on_order_save(sender, instance, created, **kwargs):
    if created:
        # Stock already decreased in serializer, no need here.
        pass
    else:
        # Handle status change if needed (like restock on cancel)
        if instance.status == 'CANCELLED':
            product = instance.product
            product.stock += instance.quantity
            product.save()

@receiver(post_delete, sender=Order)
def update_stock_on_order_delete(sender, instance, **kwargs):
    # Optional: Restock when order deleted
    product = instance.product
    product.stock += instance.quantity
    product.save()
