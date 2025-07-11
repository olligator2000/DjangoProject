from django import forms
from .models import Order, ProductReview


class OrderForm(forms.ModelForm):
    phone = forms.CharField(
        label="Телефон получателя",
        max_length=15,
        widget=forms.TextInput(attrs={'value': '+7'})
    )
    payment_method = forms.ChoiceField(
        label="Способ оплаты",
        choices=[('', 'Выберите способ оплаты'), ('card', 'Карта'), ('sbp', 'СБП')],
        required=True,
        widget=forms.HiddenInput()
    )
    delivery_time = forms.ChoiceField(
        label="Время доставки",
        choices=Order.DELIVERY_TIME_CHOICES,
        initial='now'
    )

    class Meta:
        model = Order
        fields = [
            'full_name', 'phone', 'address', 'apartment_office', 'intercom', 'entrance', 'floor',
            'courier_comment', 'order_comment', 'delivery_time', 'card_number', 'cardholder_name',
            'cvv', 'payment_method'
        ]


class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'rating-input',
            'min': '1',
            'max': '5'
        }),
        label='Оценка'
    )

    class Meta:
        model = ProductReview
        fields = ['text', 'rating']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Напишите ваш отзыв о товаре...',
                'class': 'review-textarea'
            })
        }