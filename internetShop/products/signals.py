from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ProductRating

@receiver(post_save, sender=ProductRating)
@receiver(post_delete, sender=ProductRating)
def update_product_rating(sender, instance, **kwargs):
    instance.product.update_average_rating()