from django.contrib import admin
from django.utils.html import format_html
# Register your models here.
from products.models import Product, ProductCategory, Basket

# admin.site.register(Product)
admin.site.register(ProductCategory)
admin.site.register(Basket)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'quantity', 'category', 'display_image')
    list_filter = ('category',)
    search_fields = ('name',)
    ordering = ('-name', 'price',)
    fields = ('name', 'image', 'image_preview',('price', 'quantity', 'category', 'kilocalories',
              'kilojoule', 'fats', 'carbs', 'proteins'), 'brand', 'manufacturer_country',
              'manufacturer', 'specificity', 'packing_type', 'material_type', 'size', 'composition',
              'storage_conditions', 'recommendations', 'rating',)
    # readonly_fields = ('short_description',)
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
    filter = ('product',  'quantity', 'created_timestamp')
    readonly_fields = ('created_timestamp',)