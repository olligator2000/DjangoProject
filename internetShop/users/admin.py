from django.contrib import admin
from users.models import User
from products.models import Order, OrderItem
from products.models import ProductReview
from products.admin import BasketAdminInline, OrderAdminInline
from users.models import Favorite

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ('product', 'quantity', 'price')
    extra = 1
    verbose_name = 'Товар в заказе'
    verbose_name_plural = 'Товары в заказе'

class OrderAdminInline(admin.TabularInline):
    model = Order
    fields = ('id', 'full_name', 'order_date', 'total_price', 'payment_method', 'transaction_id')
    readonly_fields = ('id', 'order_date', 'transaction_id')
    extra = 0
    verbose_name = 'Заказ'
    verbose_name_plural = 'Заказы'
    inlines = [OrderItemInline]
    can_delete = True
    show_change_link = True  # Позволяет перейти к редактированию заказа
    # Фильтры в инлайне не поддерживаются, но мы можем ограничить queryset
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('items__product')

class FavoriteInline(admin.TabularInline):
    model = Favorite
    fields = ('product', 'added_at')
    readonly_fields = ('added_at',)
    extra = 0
    verbose_name = 'Избранный товар'
    verbose_name_plural = 'Избранные товары'
    list_filter = ('added_at',)
    search_fields = ('product__name',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')

class ProductReviewInline(admin.TabularInline):
    model = ProductReview
    fields = ('product', 'text', 'created_at')
    readonly_fields = ('created_at',)
    extra = 0
    verbose_name = 'Отзыв'
    verbose_name_plural = 'Отзывы'
    list_filter = ('created_at',)
    search_fields = ('product__name', 'text')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    inlines = (BasketAdminInline, OrderAdminInline, FavoriteInline, ProductReviewInline)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active')
    list_filter = ('is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')