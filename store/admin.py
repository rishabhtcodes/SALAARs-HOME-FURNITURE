from django.contrib import admin
from .models import Category, NavCategory, Product, Cart, CartItem, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "delivery_time", "order")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description")


@admin.register(NavCategory)
class NavCategoryAdmin(admin.ModelAdmin):
    list_display = ("label", "slug", "source_category", "is_in_header", "order")
    prepopulated_fields = {"slug": ("label",)}
    list_filter = ("is_in_header",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "delivery_time", "availability", "featured", "best_selling", "is_new", "order")
    list_filter = ("category", "availability", "featured", "best_selling", "is_new")
    search_fields = ("name", "item_id", "material", "color")
    prepopulated_fields = {"slug": ("name",)}


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "session_key", "created_at", "total_count", "total_price")
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "phone", "city", "total_amount", "status", "created_at")
    list_filter = ("status", "created_at", "city")
    search_fields = ("full_name", "phone", "email", "address")
    inlines = [OrderItemInline]
