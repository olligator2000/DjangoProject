from django.shortcuts import render


def index(request):
    context = {
        "title": "store"
    }
    return render(request, "products/index.html")


def products(request):
    context = {
        "title": "store - products"
    }
    return render(request, "products/products.html")
