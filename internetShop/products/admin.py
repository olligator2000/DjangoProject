from django.contrib import admin
from django.utils.html import format_html
from products.models import Product, ProductCategory, Basket, Order, OrderItem, ProductReview

# Регистрация ProductCategory и Basket
admin.site.register(ProductCategory)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'quantity', 'category', 'display_image')
    list_filter = ('category',)
    search_fields = ('name',)
    ordering = ('-name', 'price',)
    fields = (
        'name', 'image', 'image_preview', ('price', 'quantity', 'category', 'kilocalories',
        'kilojoule', 'fats', 'carbs', 'proteins'), 'brand', 'manufacturer_country',
        'manufacturer', 'specificity', 'packing_type', 'material_type', 'size', 'composition',
        'storage_conditions', 'recommendations', 'rating',
    )
    readonly_fields = ('image_preview',)

    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "-"

    display_image.short_description = 'Image'

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="200" height="200" />', obj.image.url)
        return "-"

    image_preview.short_description = 'Image Preview'

class BasketAdminInline(admin.TabularInline):
    model = Basket
    fields = ('product', 'quantity', 'created_timestamp')
    readonly_fields = ('created_timestamp',)
    extra = 0

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ('product', 'quantity', 'price')
    extra = 1  # Добавляем одну пустую строку для нового товара
    verbose_name = 'Товар в заказе'
    verbose_name_plural = 'Товары в заказе'

class OrderAdminInline(admin.TabularInline):
    model = Order
    fields = ('user', 'total_price', 'order_date', 'payment_method')
    readonly_fields = ('order_date',)
    extra = 0  # Не показывать пустые формы

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'created_at')
    list_filter = ('created_at', 'rating')
    search_fields = ('user__username', 'product__name', 'text')
    readonly_fields = ('created_at',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'full_name', 'order_date', 'total_price', 'payment_method', 'transaction_id')
    list_filter = ('order_date', 'user__username', 'items__product__name')  # Фильтры по дате, имени пользователя и товарам
    search_fields = ('full_name', 'user__username', 'transaction_id', 'items__product__name')
    date_hierarchy = 'order_date'  # Иерархия дат для удобной навигации
    inlines = [OrderItemInline]
    readonly_fields = ('transaction_id', 'order_date')
    fields = (
        'user', 'full_name', 'phone', 'address', ('apartment_office', 'intercom', 'entrance', 'floor'),
        'courier_comment', 'order_comment', 'delivery_time', 'total_price', 'delivery_cost',
        'service_fee', 'order_date', 'payment_method', 'transaction_id', 'card_number',
        'cardholder_name', 'cvv'
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('items__product')

@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'created_timestamp')
    list_filter = ('user', 'created_timestamp')
    search_fields = ('user__username', 'product__name')
    readonly_fields = ('created_timestamp',)