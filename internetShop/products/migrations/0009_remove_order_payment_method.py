# Generated by Django 5.2 on 2025-06-16 11:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_order_payment_method'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='payment_method',
        ),
    ]
