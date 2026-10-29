from django.test import TestCase, Client
from django.urls import reverse
from store.models import Category, NavCategory, Product, Cart, CartItem, Order, FAQGroup, FAQItem
import json
import re


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
            "User-Agent: *\nAllow: /\n\nSitemap: https://salaars-home.vercel.app/sitemap.xml\n",
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
        self.assertIn('name="google-site-verification" content="yw2_qlD281fh3LxRaN6GJlQPSGfXhBRLyMVd1R1g6nQ"', content)

    def test_product_metadata_matches_reference(self):
        response = self.client.get(reverse("product_detail", args=[self.product.slug]))
        content = response.content.decode("utf-8")
        self.assertIn(
            "Bedroom Sets – Design 1 – Full bedroom suites Made by SALAAR&#x27;s HOME.",
            content,
        )
        self.assertIn('<meta property="og:title" content="Bedroom Sets – Design 1 | SALAAR&#x27;s HOME">', content)
        self.assertIn(f'<meta property="og:image" content="https://salaars-home.vercel.app/static/{self.product.image[1:]}">', content)

    def test_404_is_noindex_with_home_canonical(self):
        response = self.client.get("/this-page-does-not-exist/")
        content = response.content.decode("utf-8")
        self.assertIn('name="robots" content="noindex, follow"', content)
        self.assertIn('<link rel="canonical" href="https://salaars-home.vercel.app">', content)

    def test_sitemap_priorities(self):
        response = self.client.get(reverse("sitemap_xml"))
        content = response.content.decode("utf-8")
        self.assertIn("<priority>1</priority>", content)
        self.assertIn("<lastmod>", content)
        # Reference order: static routes, then nav categories, then categories, then products
        self.assertLess(content.index("/category/bed-sets"), content.index("/bedroom-sets"))
        self.assertIn("<loc>https://salaars-home.vercel.app/</loc>", content)
        self.assertNotIn("-ph-", content)

    def test_demo_payment_gateway_flow(self):
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
