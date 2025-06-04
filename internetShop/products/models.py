from django.db import models
from users.models import User

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
    name = models.CharField(max_length=256, verbose_name=('Имя'))
    image = models.ImageField(upload_to="product_media", verbose_name=('Фото продукции'))
    short_description = models.TextField(max_length=64, blank=True, verbose_name=('Краткое описание'))
    description = models.TextField(max_length=64, blank=True, verbose_name=('Описание'))
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=('Цена'))
    quantity = models.PositiveIntegerField(default=0, verbose_name=('Количество'))
    category = models.ForeignKey(ProductCategory, on_delete=models.PROTECT, related_name='products', verbose_name=('Категория'))
    manufacturer_country = models.CharField(max_length=24, blank=True, verbose_name=('Страна производитель'))
    manufacturer = models.CharField(max_length=24, blank=True, verbose_name=('Производитель'))
    specificity = models.TextField(max_length=512, blank=True, verbose_name=('Спецификация'))
    brand = models.TextField(max_length=24, blank=True, verbose_name=('Бренд'))
    packing_type = models.TextField(max_length=24, blank=True, verbose_name=('Тип упаковки'))
    material_type = models.TextField(max_length=24, blank=True, verbose_name=('Тип материала'))
    size = models.TextField(max_length=16, blank=True, verbose_name=('Размеры ШхВхГ'))
    composition = models.TextField(max_length=512, blank=True, verbose_name=('Состав'))
    kilocalories = models.DecimalField(max_digits=8, decimal_places=1, default=0, verbose_name=('Ккал'))
    kilojoule = models.PositiveIntegerField(default=0, verbose_name=('КДж'))
    fats = models.DecimalField(max_digits=8, decimal_places=1, default=0, verbose_name=('Жиры'))
    carbs = models.DecimalField(max_digits=5, decimal_places=1, default=0, verbose_name=('Углеводы'))
    proteins = models.DecimalField(max_digits=5, decimal_places=1, default=0, verbose_name=('Белки'))
    storage_conditions = models.TextField(max_length=64, blank=True, verbose_name=('Условия хранения'))
    recommendations  = models.TextField(max_length=1024, blank=True, verbose_name=('Рекомендации'))
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0, verbose_name=('Рейтинг'))

    def __str__(self):
        return f"{self.name} | {self.category.name}"


class Basket(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    created_timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    @property
    def sum(self):
        return int(self.product.price * self.quantity)

    def __str__(self):
        return f"Корзина для {self.user.username} | Продукт {self.product.name} | {self.quantity} шт."