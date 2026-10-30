from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse
from PIL import Image
from store.models import Category, NavCategory, Product, Cart, CartItem, Order, FAQGroup, FAQItem, UserProfile
import io
import json
import os
import re
from pathlib import Path

SITE_URL = settings.SITE_URL.rstrip("/")


class StoreViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(
            slug="bedroom-sets",
            name="Bedroom Sets",
            tagline="Complete bedroom collections",
            short="Full bedroom suites",
            description="Handcrafted solid wood bedroom sets.",
            delivery_time="7–20 days"
        )
        self.nav_cat = NavCategory.objects.create(
            slug="bed-sets",
            label="Bed Sets",
            source_category=self.category,
            tagline="Complete bedroom collections",
            short="Full bedroom suites",
            description="Handcrafted bed sets",
            is_in_header=True,
            order=0
        )
        self.product = Product.objects.create(
            item_id="bedroom-sets-1",
            slug="bedroom-sets-1",
            name="Bedroom Sets – Design 1",
            category=self.category,
            price=120000,
            image="/products/bedroom-sets/1.jpeg",
            material="Solid Wood",
            delivery_time="7–20 days",
            availability="In Stock",
            best_selling=True
        )

    def test_homepage(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "SALAAR's HOME")
        self.assertContains(response, "Timeless Furniture, Crafted for Your Home")
        self.assertContains(response, "Bedroom Sets – Design 1")

    def test_shop_page(self):
        response = self.client.get(reverse("shop"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Shop All Furniture")
        self.assertContains(response, "Bedroom Sets – Design 1")

    def test_category_page(self):
        response = self.client.get(reverse("nav_category", args=["bed-sets"]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The Bed Sets Collection")
        self.assertContains(response, "Bedroom Sets – Design 1")

    def test_direct_category_page(self):
        response = self.client.get(reverse("direct_category", args=["bedroom-sets"]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The Bedroom Sets Collection")

    def test_product_detail_page(self):
        response = self.client.get(reverse("product_detail", args=["bedroom-sets-1"]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bedroom Sets – Design 1")
        self.assertContains(response, "Add to Cart")
        self.assertContains(response, "Rs. 120,000")

    def test_static_pages(self):
        for route in ["about", "contact", "faq"]:
            res = self.client.get(reverse(route))
            self.assertEqual(res.status_code, 200)

    def test_seo_endpoints(self):
        r_res = self.client.get(reverse("robots_txt"))
        self.assertEqual(r_res.status_code, 200)
        self.assertEqual(
            r_res.content.decode("utf-8"),
            f"User-Agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n",
        )

        s_res = self.client.get(reverse("sitemap_xml"))
        self.assertEqual(s_res.status_code, 200)
        self.assertIn("<urlset", s_res.content.decode("utf-8"))
        self.assertIn("bedroom-sets-1", s_res.content.decode("utf-8"))

    def test_search_api(self):
        response = self.client.get(reverse("search_api") + "?q=Design")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(len(data["results"]) > 0)
        self.assertEqual(data["results"][0]["name"], "Bedroom Sets – Design 1")

    def test_cart_and_checkout_flow(self):
        # Create user and log in to checkout
        user = User.objects.create_user(username="checkoutuser", email="customer@example.com", password="password123")
        self.client.login(username="checkoutuser", password="password123")

        # 1. Add to cart
        add_res = self.client.post(reverse("add_to_cart", args=[self.product.id]), {"quantity": 2})
        self.assertEqual(add_res.status_code, 302)

        # 2. View cart
        cart_res = self.client.get(reverse("cart"))
        self.assertEqual(cart_res.status_code, 200)
        self.assertContains(cart_res, "Bedroom Sets – Design 1")
        self.assertContains(cart_res, "Rs. 240,000")

        # 3. Checkout POST
        checkout_res = self.client.post(reverse("checkout"), {
            "full_name": "Test Customer",
            "phone": "03001234567",
            "email": "customer@example.com",
            "city": "Delhi",
            "address": "Street 10, Kirti Nagar",
            "notes": "Handle with care",
        })
        self.assertEqual(checkout_res.status_code, 302)
        order = Order.objects.first()
        self.assertIsNotNone(order)
        self.assertEqual(order.full_name, "Test Customer")
        self.assertEqual(order.total_amount, 240000)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.user, user)

    def test_add_to_cart_requires_post(self):
        response = self.client.get(reverse("add_to_cart", args=[self.product.id]))
        self.assertEqual(response.status_code, 405)
        self.assertEqual(CartItem.objects.count(), 0)

    def test_add_to_cart_invalid_quantity_defaults_to_one(self):
        self.client.post(reverse("add_to_cart", args=[self.product.id]), {"quantity": "abc"})
        self.assertEqual(CartItem.objects.get().quantity, 1)

    def test_shop_filter_options_are_unique(self):
        for i in range(2, 5):
            Product.objects.create(
                item_id=f"bedroom-sets-{i}",
                slug=f"bedroom-sets-{i}",
                name=f"Bedroom Sets – Design {i}",
                category=self.category,
                image=f"/products/bedroom-sets/{i}.jpeg",
                material="Solid Wood",
                color="Walnut",
                delivery_time="7–20 days",
            )
        response = self.client.get(reverse("shop"))
        self.assertEqual(response.context["all_deliveries"], ["7–20 days"])
        self.assertEqual(response.context["all_materials"], ["Solid Wood"])
        self.assertEqual(response.context["all_colors"], ["Walnut"])
        html = response.content.decode("utf-8")
        self.assertEqual(html.count('name="delivery" value="7–20 days"'), 1)

    def test_product_gallery_and_related(self):
        other = Product.objects.create(
            item_id="bedroom-sets-2",
            slug="bedroom-sets-2",
            name="Bedroom Sets – Design 2",
            category=self.category,
            image="/products/bedroom-sets/2.jpeg",
        )
        response = self.client.get(reverse("product_detail", args=[self.product.slug]))
        gallery = response.context["gallery"]
        self.assertIn(self.product.image, gallery)
        self.assertIn(other.image, gallery)
        self.assertContains(response, 'id="gallery-counter"')
        self.assertContains(response, f"1 / {len(gallery)}")
        self.assertIn(other, response.context["related_products"])

    def test_faq_page_and_jsonld(self):
        group = FAQGroup.objects.create(title="Delivery Information")
        FAQItem.objects.create(group=group, question="Do you deliver?", answer="Yes, nationwide.")
        response = self.client.get(reverse("faq"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Delivery Information")
        self.assertContains(response, "Do you deliver?")
        blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', response.content.decode("utf-8"), re.S)
        faq_ld = [json.loads(b) for b in blocks if '"FAQPage"' in b][0]
        self.assertEqual(faq_ld["@type"], "FAQPage")
        names = [item["name"] for item in faq_ld["mainEntity"]]
        self.assertIn("Do you deliver?", names)

    def test_homepage_structured_data(self):
        response = self.client.get(reverse("home"))
        blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', response.content.decode("utf-8"), re.S)
        types = [json.loads(b)["@type"] for b in blocks]
        self.assertEqual(types, ["FurnitureStore", "Organization", "WebSite"])

    def test_custom_404_page(self):
        response = self.client.get("/this-page-does-not-exist/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Browse the Shop", status_code=404)
        self.assertContains(response, "404", status_code=404)

    def test_category_breadcrumb_jsonld(self):
        response = self.client.get(reverse("nav_category", args=["bed-sets"]))
        blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', response.content.decode("utf-8"), re.S)
        crumbs = [json.loads(b) for b in blocks if '"BreadcrumbList"' in b][0]
        self.assertEqual([i["name"] for i in crumbs["itemListElement"]], ["Home", "Shop", "Bed Sets"])

    def test_search_api_limit_is_eight_with_full_total(self):
        for i in range(10):
            Product.objects.create(
                item_id=f"extra-{i}",
                slug=f"extra-{i}",
                name=f"Searchable Piece {i}",
                category=self.category,
                image="/products/bedroom-sets/1.jpeg",
                availability="In Stock",
            )
        response = self.client.get(reverse("search_api") + "?q=Searchable")
        data = response.json()
        self.assertEqual(len(data["results"]), 8)
        self.assertEqual(data["total"], 10)
        self.assertEqual(data["results"][0]["price"], "–")

    def test_global_metadata(self):
        response = self.client.get(reverse("home"))
        content = response.content.decode("utf-8")
        self.assertIn('name="keywords" content="Furniture Delhi,', content)
        self.assertIn('name="robots" content="index, follow"', content)
        self.assertIn('name="googlebot" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"', content)
        self.assertNotIn('name="google-site-verification"', content)

    def test_product_metadata_matches_reference(self):
        response = self.client.get(reverse("product_detail", args=[self.product.slug]))
        content = response.content.decode("utf-8")
        self.assertIn(
            "Bedroom Sets – Design 1 – Full bedroom suites Made by SALAAR&#x27;s HOME.",
            content,
        )
        self.assertIn('<meta property="og:title" content="Bedroom Sets – Design 1 | SALAAR&#x27;s HOME">', content)
        self.assertIn(f'<meta property="og:image" content="{SITE_URL}/static/{self.product.image[1:]}">', content)

    def test_404_is_noindex_with_home_canonical(self):
        response = self.client.get("/this-page-does-not-exist/")
        content = response.content.decode("utf-8")
        self.assertIn('name="robots" content="noindex, follow"', content)
        self.assertIn(f'<link rel="canonical" href="{SITE_URL}">', content)

    def test_sitemap_priorities(self):
        response = self.client.get(reverse("sitemap_xml"))
        content = response.content.decode("utf-8")
        self.assertIn("<priority>1</priority>", content)
        self.assertIn("<lastmod>", content)
        # Reference order: static routes, then nav categories, then categories, then products
        self.assertLess(content.index("/category/bed-sets"), content.index("/bedroom-sets"))
        self.assertIn(f"<loc>{SITE_URL}/</loc>", content)
        self.assertNotIn("-ph-", content)

    def test_demo_payment_gateway_flow(self):
        # Create user and log in to checkout
        User.objects.create_user(username="payuser", email="hamza@example.com", password="password123")
        self.client.login(username="payuser", password="password123")

        # 1. Add product to cart
        self.client.post(reverse("add_to_cart", args=[self.product.id]), {"quantity": 1})

        # 2. Submit checkout with card payment method
        checkout_res = self.client.post(reverse("checkout"), {
            "full_name": "Hamza Alvi",
            "phone": "03009876543",
            "email": "hamza@example.com",
            "city": "Delhi",
            "address": "Bungalow 45, Clifton Block 4",
            "payment_method": "card",
            "notes": "Urgent bedroom setup",
        })
        order = Order.objects.latest("id")
        self.assertRedirects(checkout_res, reverse("payment_gateway", args=[order.id]))
        self.assertFalse(order.is_paid)

        # 3. View Payment Gateway
        gateway_res = self.client.get(reverse("payment_gateway", args=[order.id]))
        self.assertEqual(gateway_res.status_code, 200)
        self.assertContains(gateway_res, "SALAAR's Pay Safe Demo Gateway")
        self.assertContains(gateway_res, "Rs. 120,000")

        # 4. Authorize Payment
        pay_res = self.client.post(reverse("payment_gateway", args=[order.id]), {"action": "pay"})
        self.assertRedirects(pay_res, reverse("order_success", args=[order.id]))
        order.refresh_from_db()
        self.assertTrue(order.is_paid)
        self.assertEqual(order.status, "paid")
        self.assertTrue(order.payment_transaction_id.startswith("TXN-SLR-"))


class AuthViewsTestCase(TestCase):
    def test_auth_pages_render_with_intro(self):
        for route in ["login", "register"]:
            res = self.client.get(reverse(route))
            self.assertEqual(res.status_code, 200)
            self.assertContains(res, "Furniture chosen once,")
            self.assertContains(res, "Private Client Access")
            self.assertContains(res, reverse("login"))
            self.assertContains(res, reverse("register"))

    def test_header_shows_sign_in_for_guest(self):
        res = self.client.get(reverse("home"))
        self.assertContains(res, f'href="{reverse("login")}"')

    def test_register_creates_account_and_signs_in(self):
        res = self.client.post(reverse("register"), {
            "username": "new-client",
            "email": "new-client@example.com",
            "first_name": "New",
            "last_name": "Client",
            "password": "s3cret-pass-123",
            "confirm_password": "s3cret-pass-123",
        })
        self.assertRedirects(res, reverse("account"))
        user = User.objects.get(username="new-client")
        self.assertTrue(user.check_password("s3cret-pass-123"))

    def test_intro_page_accessible_and_links_to_auth(self):
        res = self.client.get(reverse("intro"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Welcome to SALAAR&#x27;s HOME")
        self.assertContains(res, reverse("register"))
        self.assertContains(res, reverse("login"))

    def test_unauthenticated_checkout_redirects_to_login(self):
        # Attempt GET /checkout/ without authentication
        res = self.client.get(reverse("checkout"))
        self.assertRedirects(res, f"{reverse('login')}?next={reverse('checkout')}")

    def test_account_avatar_and_delete_flow(self):
        user = User.objects.create_user("avatar_user", password="password123")
        self.client.login(username="avatar_user", password="password123")
        
        # Test Account View renders
        res = self.client.get(reverse("account"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Delete Account")
        self.assertContains(res, "Upload Profile Photo")

        # Test Delete Account View
        del_res = self.client.post(reverse("delete_account"))
        self.assertRedirects(del_res, reverse("home"))
        self.assertFalse(User.objects.filter(username="avatar_user").exists())

    def test_login_rejects_offsite_next_and_honours_local_next(self):
        User.objects.create_user("client", password="s3cret-pass-123")

        res = self.client.post(reverse("login"), {
            "username": "client",
            "password": "s3cret-pass-123",
            "next": "https://evil.example/phish",
        })
        self.assertRedirects(res, reverse("account"))
        self.client.logout()

        res = self.client.post(reverse("login"), {
            "username": "client",
            "password": "s3cret-pass-123",
            "next": reverse("cart"),
        })
        self.assertRedirects(res, reverse("cart"))


class OrderAccessControlTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        category = Category.objects.create(
            slug="bedroom-sets", name="Bedroom Sets", tagline="Complete bedroom collections",
            short="Full bedroom suites", description="Handcrafted solid wood bedroom sets.",
            material="Solid Wood", dimensions="180x200 cm",
            seo_title="Bedroom Sets", seo_description="Handcrafted bedroom sets.",
        )
        product = Product.objects.create(
            item_id="t-1", category=category, name="Teak Bed", slug="teak-bed",
            price=120000, image="/products/bedroom-sets/1.jpeg", material="Solid Teak",
            delivery_time="7 days", availability="In Stock", order=1,
        )
        self.product = product
        self.owner = User.objects.create_user("owner", password="password123")
        self.stranger = User.objects.create_user("stranger", password="password123")
        self.order = Order.objects.create(
            user=self.owner, full_name="Owner Private", phone="9800000000",
            email="owner@example.com", address="Private Lane 7", city="Delhi",
            total_amount=120000, payment_method="card",
        )

    def test_stranger_cannot_open_order_success(self):
        self.assertEqual(self.client.get(reverse("order_success", args=[self.order.id])).status_code, 404)
        self.client.login(username="stranger", password="password123")
        self.assertEqual(self.client.get(reverse("order_success", args=[self.order.id])).status_code, 404)

    def test_stranger_cannot_mark_foreign_order_paid(self):
        res = self.client.post(reverse("payment_gateway", args=[self.order.id]), {"action": "pay"})
        self.assertEqual(res.status_code, 404)
        self.order.refresh_from_db()
        self.assertFalse(self.order.is_paid)

    def test_owner_can_open_order_pages(self):
        self.client.login(username="owner", password="password123")
        self.assertEqual(self.client.get(reverse("order_success", args=[self.order.id])).status_code, 200)
        self.assertEqual(self.client.get(reverse("payment_gateway", args=[self.order.id])).status_code, 200)

    def test_checkout_session_may_view_the_order_it_just_placed(self):
        guest = Client()
        guest.login(username="owner", password="password123")
        guest.post(reverse("add_to_cart", args=[self.product.id]), {"quantity": 1})
        res = guest.post(reverse("checkout"), {
            "full_name": "Owner Private", "phone": "9800000000", "email": "owner@example.com",
            "city": "Delhi", "address": "Private Lane 7", "payment_method": "cod",
        })
        order = Order.objects.latest("id")
        self.assertRedirects(res, reverse("order_success", args=[order.id]))
        # A second browser that never placed the order is refused.
        other = Client()
        self.assertEqual(other.get(reverse("order_success", args=[order.id])).status_code, 404)


class AvatarUploadTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("pic", password="password123")
        self.client.login(username="pic", password="password123")

    def _png_upload(self, size=900, name="pic.png"):
        # Noise keeps the PNG genuinely large, the way a phone photo would be.
        image = Image.frombytes("RGB", (size, size), os.urandom(size * size * 3))
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")

    def test_non_image_is_rejected(self):
        res = self.client.post(reverse("update_avatar"), {
            "avatar": SimpleUploadedFile("x.html", b"<svg onload=alert(1)>", content_type="image/svg+xml")
        })
        self.assertRedirects(res, reverse("account"))
        self.assertEqual(UserProfile.objects.get(user=self.user).avatar_base64, "")

    def test_large_upload_is_stored_downsized(self):
        big = self._png_upload()
        self.assertGreater(len(big.read()), 500000)
        big.seek(0)
        self.client.post(reverse("update_avatar"), {"avatar": big})
        stored = UserProfile.objects.get(user=self.user).avatar_base64
        self.assertTrue(stored.startswith("data:image/jpeg;base64,"))
        self.assertLess(len(stored), 60000)

    def test_avatar_does_not_bloat_every_page(self):
        self.client.post(reverse("update_avatar"), {"avatar": self._png_upload()})
        home = self.client.get(reverse("home"))
        self.assertLess(len(home.content), 200000)


class ThemeToggleBindingTestCase(TestCase):
    """The theme button had both an inline onclick and a main.js listener, so one
    click toggled .dark twice and the theme never changed."""

    def test_theme_toggle_has_exactly_one_binding(self):
        html = self.client.get(reverse("home")).content.decode("utf-8")
        self.assertEqual(html.count('id="theme-toggle-btn"'), 1)
        self.assertNotIn('onclick="toggleThemeMode()"', html)
        self.assertNotIn("function toggleThemeMode", html)

    def test_main_js_still_owns_the_toggle(self):
        source = (Path(settings.BASE_DIR) / "static" / "js" / "main.js").read_text(encoding="utf-8")
        self.assertIn('themeToggleBtn.addEventListener("click"', source)
        self.assertEqual(source.count('classList.toggle("dark")'), 1)


class IntroRoutingTestCase(TestCase):
    def test_welcome_alias_permanently_redirects_to_intro(self):
        res = self.client.get(reverse("welcome"))
        self.assertEqual(res.status_code, 301)
        self.assertEqual(res["Location"], reverse("intro"))

    def test_intro_is_in_sitemap(self):
        res = self.client.get(reverse("sitemap_xml"))
        self.assertIn(f"<loc>{SITE_URL}/intro</loc>", res.content.decode("utf-8"))
