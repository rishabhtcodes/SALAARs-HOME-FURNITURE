from django.test import TestCase, Client
from django.urls import reverse
from store.models import Category, NavCategory, Product, Cart, CartItem, Order


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
        self.assertContains(response, "Shop Our Collection")
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
        self.assertIn("User-agent: *", r_res.content.decode("utf-8"))

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
            "city": "Karachi",
            "address": "Street 10, DHA Phase 6",
            "notes": "Handle with care",
        })
        self.assertEqual(checkout_res.status_code, 302)
        order = Order.objects.first()
        self.assertIsNotNone(order)
        self.assertEqual(order.full_name, "Test Customer")
        self.assertEqual(order.total_amount, 240000)
        self.assertEqual(order.items.count(), 1)
