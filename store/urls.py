from django.urls import path
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("shop/", views.shop_view, name="shop"),
    path("category/<slug:slug>/", views.nav_category_view, name="nav_category"),
    path("product/<slug:slug>/", views.product_detail_view, name="product_detail"),
    path("about/", views.about_view, name="about"),
    path("intro/", views.intro_view, name="intro"),
    path("welcome/", RedirectView.as_view(pattern_name="intro", permanent=True), name="welcome"),
    path("contact/", views.contact_view, name="contact"),
    path("faq/", views.faq_view, name="faq"),
    path("robots.txt", views.robots_txt_view, name="robots_txt"),
    path("sitemap.xml", views.sitemap_xml_view, name="sitemap_xml"),
    path("api/search/", views.search_api_view, name="search_api"),

    # Shopping Cart & Checkout
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:product_id>/", views.add_to_cart_view, name="add_to_cart"),
    path("cart/update/<int:item_id>/", views.update_cart_view, name="update_cart"),
    path("cart/remove/<int:item_id>/", views.remove_from_cart_view, name="remove_from_cart"),
    path("checkout/", views.checkout_view, name="checkout"),
    path("checkout/pay/<int:order_id>/", views.payment_gateway_view, name="payment_gateway"),
    path("order/<int:order_id>/success/", views.order_success_view, name="order_success"),

    # Authentication & Account
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("account/", views.account_view, name="account"),
    path("account/avatar/", views.update_profile_avatar_view, name="update_avatar"),
    path("account/delete/", views.delete_account_view, name="delete_account"),

    # Showroom Admin Web Pages (Custom Web Page for marketinghome672@gmail.com)
    path("showroom-admin/", views.admin_dashboard_view, name="admin_dashboard"),
    path("showroom-admin/products/add/", views.admin_product_add_view, name="admin_product_add"),
    path("showroom-admin/products/delete/<int:product_id>/", views.admin_product_delete_view, name="admin_product_delete"),

    # Direct category alias /<category>
    path("<slug:category>/", views.direct_category_view, name="direct_category"),
]
