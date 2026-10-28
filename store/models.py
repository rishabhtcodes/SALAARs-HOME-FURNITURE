from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=120, unique=True)
    tagline = models.CharField(max_length=255, blank=True)
    short = models.CharField(max_length=350, blank=True)
    description = models.TextField(blank=True)
    material = models.CharField(max_length=255, blank=True)
    dimensions = models.CharField(max_length=255, blank=True)
    delivery_time = models.CharField(max_length=100, default="7–20 days")
    colors = models.JSONField(default=list, blank=True)
    seo_title = models.CharField(max_length=255, blank=True)
    seo_description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class NavCategory(models.Model):
    """Represents items in the Category Navigation Bar (/category/<slug>)"""
    label = models.CharField(max_length=120)
    slug = models.SlugField(max_length=120, unique=True)
    source_category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="nav_items"
    )
    tagline = models.CharField(max_length=255, blank=True)
    short = models.CharField(max_length=350, blank=True)
    description = models.TextField(blank=True)
    empty_title = models.CharField(max_length=255, blank=True)
    empty_text = models.TextField(blank=True)
    seo_title = models.CharField(max_length=255, blank=True)
    seo_description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_in_header = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Nav Categories"
        ordering = ["order", "label"]

    def __str__(self):
        return self.label


class FAQGroup(models.Model):
    title = models.CharField(max_length=150)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "FAQ Group"
        verbose_name_plural = "FAQ Groups"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class FAQItem(models.Model):
    group = models.ForeignKey(FAQGroup, on_delete=models.CASCADE, related_name="items")
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "FAQ Item"
        verbose_name_plural = "FAQ Items"
        ordering = ["order", "id"]

    def __str__(self):
        return self.question


class Product(models.Model):
    AVAILABILITY_CHOICES = [
        ("In Stock", "In Stock"),
        ("Made to Order", "Made to Order"),
        ("Pre Order", "Pre Order"),
    ]

    item_id = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    name = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products"
    )
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    image = models.CharField(max_length=255)  # e.g. /products/bedroom-sets/1.jpeg
    gallery = models.JSONField(default=list, blank=True)  # additional image URLs
    description = models.TextField(blank=True, null=True)
    material = models.CharField(max_length=255, blank=True, null=True)
    dimensions = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=100, blank=True, null=True)
    delivery_time = models.CharField(max_length=100, default="7–20 days")
    availability = models.CharField(
        max_length=50,
        choices=AVAILABILITY_CHOICES,
        default="In Stock"
    )
    featured = models.BooleanField(default=False)
    best_selling = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    stock = models.PositiveIntegerField(default=10)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name

    @property
    def formatted_price(self):
        if self.price:
            return f"Rs. {int(self.price):,}"
        return "Price on request"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart {self.id} ({self.user.username if self.user else self.session_key})"

    @property
    def total_count(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        total = 0
        for item in self.items.all():
            if item.product.price:
                total += item.product.price * item.quantity
        return total


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("cart", "product")

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def subtotal(self):
        if self.product.price:
            return self.product.price * self.quantity
        return 0


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending Payment / Verification"),
        ("paid", "Paid (Demo Gateway)"),
        ("confirmed", "Confirmed"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("card", "Credit / Debit Card (Demo Secure Gateway)"),
        ("jazzcash", "JazzCash / EasyPaisa (Mobile Wallet)"),
        ("bank_transfer", "Direct Showroom Bank Wire"),
        ("cod", "Cash on Delivery / Assembly"),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=50)
    email = models.EmailField(blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100, default="Karachi")
    notes = models.TextField(blank=True)
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES, default="card")
    is_paid = models.BooleanField(default=False)
    payment_transaction_id = models.CharField(max_length=100, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.id} - {self.full_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    product_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product_name}"
