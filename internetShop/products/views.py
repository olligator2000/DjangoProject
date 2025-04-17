from django.shortcuts import render
from products.models import Product, ProductCategory


def index(request):
    context = {
        "title": "store",
        "products": Product.objects.all(),
        "categories": ProductCategory.objects.all(),
    }
    return render(request, "products/index.html", context)


def products(request):
    context = {
        "title": "store - products",

    }
    return render(request, "products/products.html", context)
