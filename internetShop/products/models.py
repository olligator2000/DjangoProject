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


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=100, verbose_name='Имя получателя')
    phone = models.CharField(max_length=15, verbose_name='Телефон получателя')
    address = models.TextField(verbose_name='Адрес доставки')
    apartment_office = models.CharField(max_length=10, blank=True, verbose_name='Кв./офис')
    intercom = models.CharField(max_length=10, blank=True, verbose_name='Домофон')
    entrance = models.CharField(max_length=10, blank=True, verbose_name='Подъезд')
    floor = models.CharField(max_length=10, blank=True, verbose_name='Этаж')
    courier_comment = models.TextField(blank=True, verbose_name='Комментарий курьеру')
    order_comment = models.TextField(blank=True, verbose_name='Комментарий к заказу')
    delivery_time = models.CharField(max_length=50, blank=True, verbose_name='Время доставки')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Общая цена')
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Цена за доставку')
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, default=39, verbose_name='Сервисный сбор')
    order_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата заказа')
    card_number = models.CharField(max_length=16, blank=True, verbose_name='Номер карты клиента')
    cardholder_name = models.CharField(max_length=100, blank=True, verbose_name='Имя и фамилия на карте')
    cvv = models.CharField(max_length=4, blank=True, verbose_name='CVV карты')

    def __str__(self):
        return f"Заказ #{self.id} от {self.full_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Товар')
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Цена за единицу')

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"