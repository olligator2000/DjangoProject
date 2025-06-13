from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'full_name', 'phone', 'address', 'apartment_office', 'intercom', 'entrance', 'floor',
            'courier_comment', 'order_comment', 'delivery_time', 'card_number', 'cardholder_name',
            'cvv', 'total_price', 'delivery_cost', 'service_fee'
        ]