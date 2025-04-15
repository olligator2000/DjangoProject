from django.db import models

# Create your models here.
#Модель = Таблица


class ProductCategory(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=256)
    image = models.ImageField(upload_to="product_media")
    description = models.TextField(blank=True)
    short_description = models.TextField(max_length=64, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(ProductCategory, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name} | {self.category.name}"
