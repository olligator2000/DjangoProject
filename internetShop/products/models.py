from django.db import models

# Create your models here.
#Модель = Таблица


class ProductCategory(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=256)
    image = models.ImageField(upload_to="product_media")
    short_description = models.TextField(max_length=64, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(ProductCategory, on_delete=models.PROTECT, related_name='products')
    manufacturer_country = models.CharField(max_length=24, blank=True)
    manufacturer = models.CharField(max_length=24, blank=True)
    specificity = models.TextField(max_length=512, blank=True)
    brand = models.TextField(max_length=24, blank=True)
    packing_type = models.TextField(max_length=24, blank=True)
    material_type = models.TextField(max_length=24, blank=True)
    size = models.TextField(max_length=16, blank=True)
    composition = models.TextField(max_length=512, blank=True)
    kilocalories = models.DecimalField(max_digits=8, decimal_places=1, default=0)
    kilojoule = models.PositiveIntegerField(default=0)
    fats = models.DecimalField(max_digits=8, decimal_places=1, default=0)
    carbs = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    proteins = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    storage_conditions = models.TextField(max_length=64, blank=True)
    recommendations  = models.TextField(max_length=1024, blank=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0)

    def __str__(self):
        return f"{self.name} | {self.category.name}"
