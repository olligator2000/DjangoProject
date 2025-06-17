from django.contrib import admin
from users.models import User
from products.admin import BasketAdminInline
from products.models import Order, OrderItem

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

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    inlines = (BasketAdminInline, OrderAdminInline)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active')
    list_filter = ('is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')