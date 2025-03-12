from django.contrib import admin
from .models import Category, Product, Cart, Order, Transaction

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(Transaction)
