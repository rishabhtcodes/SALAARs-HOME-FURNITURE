from django.conf import settings
from .models import NavCategory, Category, Cart

SITE = {
    "name": "SALAAR's HOME",
    "tagline": "Premium Furniture Showroom",
    "tagline_short": "Premium Furniture",
    "url": settings.SITE_URL.rstrip("/"),
    "description": "SALAAR's HOME is a premium furniture showroom in Karachi, Pakistan offering handcrafted bedroom sets, beds, wardrobes, side tables and dressers in solid wood. Luxury wooden furniture delivered nationwide with professional assembly.",
    "keywords": [
        "Furniture Karachi",
        "Bedroom Sets Karachi",
        "Beds Karachi",
        "Wardrobes Karachi",
        "Side Tables Karachi",
        "Dressers Karachi",
        "Wooden Furniture Karachi",
        "Luxury Furniture Karachi",
        "Premium Furniture Pakistan",
        "SALAAR's HOME",
    ],
    "phone_display": settings.SITE_PHONE_DISPLAY,
    "phone_intl": settings.SITE_PHONE_INTL,
    "address": settings.SITE_ADDRESS,
    "hours": settings.SITE_HOURS,
    "maps_url": "https://www.google.com/maps/search/?api=1&query=Furniture+Showroom",
    "map_embed": "https://www.google.com/maps?q=Furniture+Showroom&output=embed",
    "facebook": settings.SITE_FACEBOOK,
    "tiktok": settings.SITE_TIKTOK,
    "whatsapp_message": "Hello SALAAR's HOME! I'm interested in your furniture.",
}


def site_context(request):
    header_categories = NavCategory.objects.filter(is_in_header=True).order_by("order")
    all_nav_categories = NavCategory.objects.all().order_by("order")
    categories = Category.objects.all().order_by("order")

    cart_count = 0
    cart = None
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    elif request.session.session_key:
        cart = Cart.objects.filter(session_key=request.session.session_key).first()

    if cart:
        cart_count = cart.total_count

    return {
        "SITE": SITE,
        "HEADER_CATEGORIES": header_categories,
        "ALL_NAV_CATEGORIES": all_nav_categories,
        "CATEGORIES": categories,
        "cart_count": cart_count,
        "current_path": request.path,
        "canonical_path": request.path.rstrip("/"),
    }
