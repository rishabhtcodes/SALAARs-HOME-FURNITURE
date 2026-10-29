from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404, HttpResponse
from django.utils import timezone
from django.db.models import Q, F
from django.db.models.functions import Lower
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import (
    Category,
    NavCategory,
    FAQGroup,
    Product,
    Cart,
    CartItem,
    Order,
    OrderItem,
)
from .forms import CheckoutForm, RegisterForm
from .emails import send_order_confirmation_email
import re


_PRICE_TOKEN_RE = re.compile(r"^(\d+(?:\.\d+)?)\s*(tr|trieu|triệu|m|milion|million|k|nghin)?$")


def parse_price_token(token):
    value = token.replace(",", ".").strip().lower()
    match = _PRICE_TOKEN_RE.match(value)
    if not match:
        return None
    amount = float(match.group(1))
    unit = match.group(2)
    if unit in ("tr", "trieu", "triệu", "m", "milion", "million"):
        amount *= 1_000_000
    elif unit in ("k", "nghin"):
        amount *= 1_000
    return amount


def product_search_filter(query):
    search = (
        Q(name__icontains=query)
        | Q(category__name__icontains=query)
        | Q(category__short__icontains=query)
        | Q(material__icontains=query)
        | Q(delivery_time__icontains=query)
        | Q(color__icontains=query)
        | Q(description__icontains=query)
    )

    token = parse_price_token(query)
    if token is not None and token.is_integer():
        search |= Q(price=token)

    digits = re.sub(r"\D", "", query)
    if digits:
        price_ids = [
            p.id
            for p in Product.objects.exclude(price=None).only("id", "price")
            if digits in f"{int(p.price):,}"
        ]
        if price_ids:
            search |= Q(id__in=price_ids)

    return search


def search_products(query, limit=None):
    matches = list(
        Product.objects.filter(product_search_filter(query)).select_related("category")
    )
    if not query:
        return matches, len(matches)

    needle = query.lower()
    matches.sort(
        key=lambda p: (
            -(
                (3 if needle in p.name.lower() else 0)
                + 1
                + (2 if p.best_selling else 0)
                + (1 if p.featured else 0)
                + (1 if p.is_new else 0)
            ),
            -(p.order or 0),
        )
    )
    total = len(matches)
    return (matches[:limit] if limit else matches), total


def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        # Migrate anonymous cart if present
        if request.session.session_key:
            anon_cart = Cart.objects.filter(session_key=request.session.session_key).first()
            if anon_cart and anon_cart != cart:
                for item in anon_cart.items.all():
                    cart_item, created = CartItem.objects.get_or_create(
                        cart=cart, product=item.product,
                        defaults={"quantity": item.quantity}
                    )
                    if not created:
                        cart_item.quantity += item.quantity
                        cart_item.save()
                anon_cart.delete()
        return cart
    else:
        if not request.session.session_key:
            request.session.save()
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
        return cart


def home_view(request):
    categories = Category.objects.all().order_by("order")

    active_tab = request.GET.get("tab", "all")
    best_seller_qs = Product.objects.all()
    if active_tab != "all" and Product.objects.filter(category__slug=active_tab).exists():
        best_seller_qs = best_seller_qs.filter(category__slug=active_tab)
    else:
        active_tab = "all"

    # Best sellers (limit 8, prioritized best_selling)
    best_sellers = best_seller_qs.order_by("-best_selling", "order")[:8]
    
    # Pack featured categories with product count and first product image
    featured_cats = []
    for cat in categories:
        first_p = cat.products.first()
        featured_cats.append({
            "slug": cat.slug,
            "name": cat.name,
            "image": first_p.image if first_p else None,
            "count": cat.products.count()
        })

    context = {
        "featured_categories": featured_cats,
        "best_selling_products": best_sellers,
        "active_tab": active_tab,
    }
    return render(request, "pages/home.html", context)


def shop_view(request):
    products = Product.objects.all()
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "all")
    price_range = request.GET.get("price", "any")
    sort = request.GET.get("sort", "newest")
    delivery = request.GET.getlist("delivery")
    material = request.GET.getlist("material")
    color = request.GET.getlist("color")
    availability = request.GET.get("availability", "all")
    tags = request.GET.getlist("tag")

    if query:
        products = products.filter(product_search_filter(query))

    if category_slug != "all":
        products = products.filter(category__slug=category_slug)

    if price_range == "lt10":
        products = products.filter(price__lt=50000)
    elif price_range == "10-30":
        products = products.filter(price__gte=50000, price__lt=150000)
    elif price_range == "30-60":
        products = products.filter(price__gte=150000, price__lt=300000)
    elif price_range == "gt60":
        products = products.filter(price__gte=300000)

    if delivery:
        products = products.filter(delivery_time__in=delivery)
    if material:
        products = products.filter(material__in=material)
    if color:
        products = products.filter(color__in=color)

    if availability != "all":
        products = products.filter(availability=availability)

    if "featured" in tags:
        products = products.filter(featured=True)
    if "bestSelling" in tags:
        products = products.filter(best_selling=True)
    if "isNew" in tags:
        products = products.filter(is_new=True)

    if sort == "oldest":
        products = products.order_by("order", "id")
    elif sort == "price-asc":
        products = products.order_by(F("price").asc(nulls_last=True), "order")
    elif sort == "price-desc":
        products = products.order_by(F("price").desc(nulls_last=True), "order")
    elif sort == "az":
        products = products.order_by(Lower("name"))
    elif sort == "za":
        products = products.order_by(Lower("name").desc())
    else:
        sort = "newest"
        products = products.order_by("-order", "-id")

    def distinct_in_order(field):
        values = []
        for value in Product.objects.order_by("order", "id").values_list(field, flat=True):
            if value and value not in values:
                values.append(value)
        return values

    all_deliveries = distinct_in_order("delivery_time")
    all_materials = distinct_in_order("material")
    all_colors = distinct_in_order("color")

    has_active_filters = bool(
        query
        or category_slug != "all"
        or price_range != "any"
        or delivery
        or material
        or color
        or availability != "all"
        or tags
    )

    context = {
        "products": products,
        "product_count": products.count(),
        "query": query,
        "active_category": category_slug,
        "price_range": price_range,
        "selected_deliveries": delivery,
        "selected_materials": material,
        "selected_colors": color,
        "selected_availability": availability,
        "selected_tags": tags,
        "sort": sort,
        "all_deliveries": all_deliveries,
        "all_materials": all_materials,
        "all_colors": all_colors,
        "has_active_filters": has_active_filters,
        "price_ranges": [
            ("any", "Any price"),
            ("lt10", "Under 50K"),
            ("10-30", "50K – 150K"),
            ("30-60", "150K – 300K"),
            ("gt60", "Above 300K"),
        ],
        "availability_options": [
            ("all", "All"),
            ("In Stock", "In Stock"),
            ("Made to Order", "Made to Order"),
        ],
        "tag_options": [
            ("featured", "Featured"),
            ("bestSelling", "Best Selling"),
            ("isNew", "Latest"),
        ],
        "breadcrumbs": [
            {"label": "Home", "url": "/"},
            {"label": "Shop All Furniture"},
        ],
    }
    return render(request, "pages/shop.html", context)


def nav_category_view(request, slug):
    nav_item = get_object_or_404(NavCategory, slug=slug)
    products = []
    if nav_item.source_category:
        products = nav_item.source_category.products.all().order_by("order")

    context = {
        "item": nav_item,
        "products": products,
        "breadcrumbs": [
            {"label": "Home", "url": "/"},
            {"label": "Shop", "url": "/shop"},
            {"label": nav_item.label},
        ],
    }
    return render(request, "pages/category.html", context)


def direct_category_view(request, category):
    cat = get_object_or_404(Category, slug=category)
    products = cat.products.all().order_by("order")
    context = {
        "info": cat,
        "products": products,
        "breadcrumbs": [
            {"label": "Home", "url": "/"},
            {"label": "Shop", "url": "/shop"},
            {"label": cat.name},
        ],
    }
    return render(request, "pages/direct_category.html", context)


def product_detail_view(request, slug):
    product = get_object_or_404(Product, slug=slug)

    related = list(
        Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    )
    if len(related) < 4:
        ids = [product.id] + [p.id for p in related]
        related += list(
            Product.objects.exclude(id__in=ids).order_by("order", "id")[: 4 - len(related)]
        )

    gallery = []
    for image in [product.image, *(product.gallery or [])]:
        if image and image not in gallery:
            gallery.append(image)
    for image in product.category.products.values_list("image", flat=True):
        if image and image not in gallery:
            gallery.append(image)

    context = {
        "product": product,
        "related_products": related,
        "gallery": gallery,
        "thumbnails": gallery[:8],
        "breadcrumb_items": [
            {"label": "Home", "url": "/"},
            {"label": "Shop", "url": "/shop"},
            {"label": product.category.name, "url": f"/{product.category.slug}"},
            {"label": product.name},
        ],
    }
    return render(request, "pages/product_detail.html", context)


def about_view(request):
    return render(
        request,
        "pages/about.html",
        {
            "breadcrumb_items": [
                {"label": "Home", "url": "/"},
                {"label": "Furnishing Homes With Care"},
            ]
        },
    )


def contact_view(request):
    return render(
        request,
        "pages/contact.html",
        {
            "breadcrumb_items": [
                {"label": "Home", "url": "/"},
                {"label": "Contact Us"},
            ]
        },
    )


def faq_view(request):
    groups = FAQGroup.objects.prefetch_related("items").all()
    faq_items = [item for group in groups for item in group.items.all()]
    context = {
        "faq_groups": groups,
        "faq_items": faq_items,
        "breadcrumb_items": [
            {"label": "Home", "url": "/"},
            {"label": "Frequently Asked Questions"},
        ],
    }
    return render(request, "pages/faq.html", context)


def search_api_view(request):
    query = request.GET.get("q", "").strip()
    if len(query) < 1:
        return JsonResponse({"results": [], "total": 0})

    matches, total = search_products(query, limit=8)

    results = []
    for p in matches:
        results.append({
            "id": p.id,
            "name": p.name,
            "slug": p.slug,
            "category": p.category.name,
            "price": f"Rs. {int(p.price):,}" if p.price else "–",
            "image": p.image,
            "delivery": p.delivery_time,
        })
    return JsonResponse({"results": results, "total": total})


def cart_view(request):
    cart = get_or_create_cart(request)
    context = {
        "cart": cart,
        "items": cart.items.select_related("product").all()
    }
    return render(request, "pages/cart.html", context)


@require_POST
def add_to_cart_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_or_create_cart(request)

    try:
        qty = max(1, int(request.POST.get("quantity", 1)))
    except (TypeError, ValueError):
        qty = 1
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, product=product,
        defaults={"quantity": qty}
    )
    if not created:
        cart_item.quantity += qty
        cart_item.save()

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "total_count": cart.total_count,
            "message": f"Added {product.name} to cart"
        })
    messages.success(request, f"Added {product.name} to your cart.")
    return redirect("cart")


@require_POST
def update_cart_view(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart = get_or_create_cart(request)
    if cart_item.cart != cart:
        raise Http404

    try:
        qty = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        qty = 1
    if qty > 0:
        cart_item.quantity = qty
        cart_item.save()
    else:
        cart_item.delete()

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "total_count": cart.total_count,
            "total_price": float(cart.total_price),
            "subtotal": float(cart_item.subtotal) if qty > 0 else 0
        })
    return redirect("cart")


@require_POST
def remove_from_cart_view(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart = get_or_create_cart(request)
    if cart_item.cart != cart:
        raise Http404

    cart_item.delete()
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "total_count": cart.total_count,
            "total_price": float(cart.total_price)
        })
    messages.info(request, "Item removed from your cart.")
    return redirect("cart")


def checkout_view(request):
    cart = get_or_create_cart(request)
    items = cart.items.select_related("product").all()
    if not items:
        messages.warning(request, "Your cart is empty. Please add items before checking out.")
        return redirect("shop")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.total_amount = cart.total_price
            order.save()

            for it in items:
                OrderItem.objects.create(
                    order=order,
                    product=it.product,
                    product_name=it.product.name,
                    price=it.product.price,
                    quantity=it.quantity
                )

            # Clear cart
            cart.items.all().delete()

            # If user selected card or mobile wallet, redirect to the interactive demo gateway
            if order.payment_method in ("card", "upi"):
                return redirect("payment_gateway", order_id=order.id)

            # Send customized order confirmation email for cash / bank wire orders
            send_order_confirmation_email(order)
            return redirect("order_success", order_id=order.id)
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {
                "full_name": f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                "email": request.user.email,
            }
        form = CheckoutForm(initial=initial)

    context = {
        "cart": cart,
        "items": items,
        "form": form,
    }
    return render(request, "pages/checkout.html", context)


def order_success_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "pages/order_success.html", {"order": order})


def payment_gateway_view(request, order_id):
    import uuid
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        action = request.POST.get("action", "pay")
        if action == "pay":
            order.is_paid = True
            order.status = "paid"
            order.payment_transaction_id = f"TXN-SLR-{uuid.uuid4().hex[:10].upper()}"
            order.save()
            send_order_confirmation_email(order)
            messages.success(request, f"Payment simulated successfully! Transaction ID: {order.payment_transaction_id}")
            return redirect("order_success", order_id=order.id)
        elif action == "cancel":
            send_order_confirmation_email(order)
            messages.info(request, "Payment was postponed. You can pay via showroom bank transfer or cash on arrival.")
            return redirect("order_success", order_id=order.id)

    context = {
        "order": order,
        "items": order.items.all(),
    }
    return render(request, "pages/payment_gateway.html", context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect("account")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            get_or_create_cart(request)  # migrates anonymous cart
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get("next", "account")
            return redirect(next_url)
    else:
        form = AuthenticationForm()

    return render(request, "pages/login.html", {"form": form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("account")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            login(request, user)
            get_or_create_cart(request)
            messages.success(request, "Your account has been created successfully!")
            return redirect("account")
    else:
        form = RegisterForm()

    return render(request, "pages/register.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("home")


@login_required
def account_view(request):
    orders = Order.objects.filter(user=request.user).prefetch_related("items").all()
    return render(request, "pages/account.html", {"orders": orders})


def not_found_view(request, exception=None):
    return render(request, "pages/404.html", status=404)


def robots_txt_view(request):
    lines = [
        "User-Agent: *",
        "Allow: /",
        "",
        f"Sitemap: {settings.SITE_URL.rstrip('/')}/sitemap.xml",
        "",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def sitemap_xml_view(request):
    base_url = settings.SITE_URL.rstrip("/")
    lastmod = timezone.now().isoformat(timespec="milliseconds").replace("+00:00", "Z")

    routes = [
        ("/", "weekly", "1"),
        ("/shop", "weekly", "0.9"),
        ("/contact", "monthly", "0.7"),
        ("/faq", "monthly", "0.6"),
        ("/about", "monthly", "0.5"),
    ]
    urls = [(f"{base_url}{path}", freq, priority) for path, freq, priority in routes]

    for cat in NavCategory.objects.order_by("order"):
        urls.append((f"{base_url}/category/{cat.slug}", "weekly", "0.8"))

    for cat in Category.objects.order_by("order"):
        urls.append((f"{base_url}/{cat.slug}", "weekly", "0.9"))

    for prod in Product.objects.exclude(item_id__contains="-ph-").order_by("order"):
        urls.append((f"{base_url}/product/{prod.slug}", "monthly", "0.7"))

    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    for loc, freq, priority in urls:
        xml_lines.append(
            f"  <url><loc>{loc}</loc><lastmod>{lastmod}</lastmod>"
            f"<changefreq>{freq}</changefreq><priority>{priority}</priority></url>"
        )
    xml_lines.append('</urlset>')

    return HttpResponse("\n".join(xml_lines), content_type="application/xml")
