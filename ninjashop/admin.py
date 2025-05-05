from django.contrib import admin
from .models import Category, Product, Wishlist, Order, OrderItem, Status


admin.site.register(Status)

class WishlistAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'quantity']
admin.site.register(Wishlist, WishlistAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
admin.site.register(Category, CategoryAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug', 'price', 'description', 'image']
    prepopulated_fields = {'slug': ('name',)}
admin.site.register(Product, ProductAdmin)


class OrderItemAdmin(admin.StackedInline):
    extra = 0
    model = OrderItem
    fields = ['product', 'cost', 'quantity']


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at', 'status', 'total']
    inlines = [OrderItemAdmin]
admin.site.register(Order, OrderAdmin)