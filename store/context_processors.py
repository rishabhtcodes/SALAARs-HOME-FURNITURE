from .models import NavCategory, Category, Cart

SITE = {
    "name": "SALAAR's HOME",
    "tagline": "Premium Furniture Showroom",
    "tagline_short": "Premium Furniture",
    "url": "https://salaars-home.vercel.app",
    "description": "SALAAR's HOME is a premium furniture showroom in Karachi, Pakistan offering handcrafted bedroom sets, beds, wardrobes, side tables and dressers in solid wood. Luxury wooden furniture delivered nationwide with professional assembly.",
    "phone": "0370804453",
    "phone_display": "037 080 4453",
    "phone_intl": "92370804453",
    "address": "Furniture Showroom",
    "hours": "Every day · 8:00 AM – 9:00 PM",
    "facebook": "https://www.facebook.com/profile.php?id=61590742701515",
    "tiktok": "https://www.tiktok.com/@salaars_farnichar",
    "whatsapp_message": "Hello SALAAR's HOME, I would like to inquire about your furniture collection.",
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
    }
