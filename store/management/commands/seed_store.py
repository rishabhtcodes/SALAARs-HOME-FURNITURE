import json
import re
from django.core.management.base import BaseCommand
from store.models import Category, NavCategory, Product

CATEGORIES_DATA = [
    {
        "slug": "bedroom-sets",
        "name": "Bedroom Sets",
        "tagline": "Complete bedroom collections, perfectly matched",
        "short": "Full bedroom suites – bed, wardrobe, dresser and side tables designed to work as one harmonious set.",
        "description": "A bedroom set from SALAAR's HOME turns an empty room into a complete, elegant retreat. Every set is designed as one cohesive collection – bed, wardrobe, dresser and side tables – so the finish, hardware and style always match perfectly. Choose from classic wood tones or modern minimal designs, all handcrafted from solid wood with premium fittings.",
        "material": "Solid wood (oak, acacia or walnut finish) with premium MDF accents and smooth, durable lacquer.",
        "dimensions": "Sets are made in full, queen and king sizes – exact dimensions vary by model.",
        "delivery_time": "7–20 days",
        "colors": ["Walnut", "Natural Oak", "Smoked Oak", "Mahogany"],
        "seo_title": "Bedroom Sets – Complete Collections",
        "seo_description": "Explore handcrafted bedroom sets at SALAAR's HOME – beds, wardrobes, dressers and side tables designed as complete, matching collections.",
        "order": 0,
    },
    {
        "slug": "wardrobes",
        "name": "Wardrobes",
        "tagline": "Storage that keeps your space beautiful",
        "short": "Spacious wardrobes with sliding or hinged doors, built-in mirrors and smart internal storage.",
        "description": "A well-designed wardrobe quietly keeps your home organized and calm. Our wardrobes combine generous storage with clean, beautiful lines – soft-close doors, adjustable shelves, drawers and hanging space for everything you own. From slim two-door designs to full wall-to-wall wardrobes, every piece is built to last a lifetime.",
        "material": "Solid wood frame with premium laminate or lacquer finishes and soft-close hardware.",
        "dimensions": "From 1.2 m to 2.4 m wide, 2.1 m to 2.7 m tall – custom dimensions available.",
        "delivery_time": "7–20 days",
        "colors": ["Walnut", "Natural Oak", "Mahogany", "White Gloss"],
        "seo_title": "Wardrobes – Spacious & Elegant Storage",
        "seo_description": "Discover quality wardrobes at SALAAR's HOME – sliding and hinged door designs, smart internal storage, made to measure.",
        "order": 1,
    },
    {
        "slug": "side-tables",
        "name": "Side Tables",
        "tagline": "Small pieces, big character",
        "short": "Elegant bedside and accent tables in solid wood – the finishing touch for any room.",
        "description": "The right side table finishes a room. Handcrafted from solid wood with clean joins and smooth finishes, our side tables bring warmth and function to the bedside, the sofa corner or the hallway. Available in a range of heights and styles to match any interior – simple, elegant and built to last.",
        "material": "Solid wood tops with durable lacquer finish; metal or wood legs depending on design.",
        "dimensions": "Approx. 40 x 40 x 55 cm – multiple styles and heights available.",
        "delivery_time": "1–3 days",
        "colors": ["Natural Oak", "Walnut", "Light Oak", "Black"],
        "seo_title": "Side Tables – Elegant Accent Pieces",
        "seo_description": "Shop elegant solid wood side tables at SALAAR's HOME – bedside and accent tables in many styles and finishes.",
        "order": 2,
    },
    {
        "slug": "dressers-mirrors",
        "name": "Dressers & Mirrors",
        "tagline": "Where beauty meets everyday function",
        "short": "Dressers with storage plus matching mirrors – a classic, elegant corner for your room.",
        "description": "A dresser is more than a place to get ready in the morning – it is a statement piece. Our dressers offer deep, smooth-gliding drawers for all your essentials, topped with a beautiful vanity mirror that completes the look. Classic and contemporary designs available in rich wood tones that grow more beautiful with age.",
        "material": "Solid wood construction with hand-finished lacquer and premium mirror glass.",
        "dimensions": "Dressers approx. 120 x 45 x 80 cm; mirrors approx. 90 x 110 cm – models vary.",
        "delivery_time": "3–7 days",
        "colors": ["Walnut", "Mahogany", "Natural Oak", "White Gloss"],
        "seo_title": "Dressers & Mirrors – Classic Vanity Pieces",
        "seo_description": "Browse dressers and vanity mirrors at SALAAR's HOME – classic wooden dressers with elegant matching mirrors.",
        "order": 3,
    },
]

NAV_CATEGORIES_DATA = [
    {
        "slug": "bed-sets",
        "label": "Bed Sets",
        "source_slug": "bedroom-sets",
        "tagline": "Complete bedroom collections, perfectly matched",
        "short": "Full bedroom suites – bed, wardrobe, dresser and side tables designed to work as one harmonious set.",
        "description": "A bed set from SALAAR's HOME turns an empty room into a complete, elegant retreat. Every set is designed as one cohesive collection – bed, wardrobe, dresser and side tables – so the finish, hardware and style always match perfectly. Choose from classic wood tones or modern minimal designs, all handcrafted from solid wood with premium fittings.",
        "seo_title": "Bed Sets – Complete Bedroom Collections",
        "seo_description": "Explore handcrafted bed sets at SALAAR's HOME – beds, wardrobes, dressers and side tables designed as complete, matching collections.",
        "order": 0,
        "is_in_header": True,
    },
    {
        "slug": "beds",
        "label": "Beds",
        "source_slug": "bedroom-sets",
        "tagline": "The heart of your bedroom",
        "short": "Beautiful solid-wood beds – queen, king and custom sizes – built for comfort and made to last.",
        "description": "A great bed anchors the whole bedroom. Our beds are built from solid wood with reinforced frames and elegant headboards, available in queen, king and custom sizes. Whether you prefer a classic panel design or a modern upholstered silhouette, every bed is finished by hand and delivered with professional assembly.",
        "seo_title": "Beds – Solid Wood Beds for Every Bedroom",
        "seo_description": "Discover quality solid-wood beds at SALAAR's HOME – queen, king and custom sizes, handcrafted and delivered with assembly.",
        "order": 1,
        "is_in_header": True,
    },
    {
        "slug": "side-tables",
        "label": "Side Tables",
        "source_slug": "side-tables",
        "tagline": "Small pieces, big character",
        "short": "Elegant bedside and accent tables in solid wood – the finishing touch for any room.",
        "description": "The right side table finishes a room. Handcrafted from solid wood with clean joins and smooth finishes, our side tables bring warmth and function to the bedside, the sofa corner or the hallway. Available in a range of heights and styles to match any interior – simple, elegant and built to last.",
        "seo_title": "Side Tables – Elegant Accent Pieces",
        "seo_description": "Shop elegant solid wood side tables at SALAAR's HOME – bedside and accent tables in many styles and finishes.",
        "order": 2,
        "is_in_header": True,
    },
    {
        "slug": "dressers",
        "label": "Dressers",
        "source_slug": "dressers-mirrors",
        "tagline": "Where beauty meets everyday function",
        "short": "Dressers with deep, smooth-gliding drawers – classic storage for your everyday essentials.",
        "description": "A dresser is more than a place to get ready in the morning – it is a statement piece. Our dressers offer deep, smooth-gliding drawers for all your essentials, topped with a beautiful vanity mirror that completes the look. Classic and contemporary designs available in rich wood tones that grow more beautiful with age.",
        "seo_title": "Dressers – Classic Storage With Elegance",
        "seo_description": "Browse classic wooden dressers at SALAAR's HOME – deep smooth-gliding drawers and hand-finished solid wood.",
        "order": 3,
        "is_in_header": True,
    },
    {
        "slug": "mirrors",
        "label": "Mirrors",
        "source_slug": "dressers-mirrors",
        "tagline": "Reflections that elevate a room",
        "short": "Elegant standing and vanity mirrors that add light, depth and character to any space.",
        "description": "The right mirror makes a room feel larger, brighter and more composed. Our mirrors pair premium mirror glass with hand-finished wooden frames – from slim vanity mirrors to full-length standing designs. Each piece is carefully packed and delivered with care.",
        "seo_title": "Mirrors – Premium Framed Vanity Mirrors",
        "seo_description": "Discover premium mirrors at SALAAR's HOME – vanity and standing mirrors with hand-finished wooden frames.",
        "order": 4,
        "is_in_header": True,
    },
    {
        "slug": "wardrobes",
        "label": "Wardrobes",
        "source_slug": "wardrobes",
        "tagline": "Storage that keeps your space beautiful",
        "short": "Spacious wardrobes with sliding or hinged doors, built-in mirrors and smart internal storage.",
        "description": "A well-designed wardrobe quietly keeps your home organized and calm. Our wardrobes combine generous storage with clean, beautiful lines – soft-close doors, adjustable shelves, drawers and hanging space for everything you own. From slim two-door designs to full wall-to-wall wardrobes, every piece is built to last a lifetime.",
        "seo_title": "Wardrobes – Spacious & Elegant Storage",
        "seo_description": "Discover quality wardrobes at SALAAR's HOME – sliding and hinged door designs, smart internal storage, made to measure.",
        "order": 5,
        "is_in_header": True,
    },
    {
        "slug": "tv-units",
        "label": "TV Units",
        "source_slug": None,
        "tagline": "The centerpiece of your living room",
        "short": "Elegant TV stands and entertainment units with smart cable management and generous storage.",
        "description": "A beautifully crafted TV unit keeps your living room tidy and stylish. Our entertainment units combine clean lines, soft-close drawers and smart cable management – designed to hold today's screens while complementing your decor. New designs are added regularly.",
        "empty_title": "This collection is coming soon",
        "empty_text": "We are crafting a new selection of TV units. Meanwhile, our team can build a custom piece to your exact size and finish – just ask.",
        "seo_title": "TV Units – Elegant Entertainment Storage",
        "seo_description": "TV units at SALAAR's HOME – elegant entertainment stands with smart storage, arriving soon. Custom sizes available.",
        "order": 6,
        "is_in_header": False,
    },
    {
        "slug": "study-tables",
        "label": "Study Tables",
        "source_slug": None,
        "tagline": "A calm corner to think and work",
        "short": "Solid-wood study desks with clean lines, cable management and room to focus.",
        "description": "The right desk turns a corner into a workspace. Our study tables pair solid wood surfaces with clean, minimalist legs and practical cable management – made for focus, made to last. New designs are added regularly.",
        "empty_title": "This collection is coming soon",
        "empty_text": "We are crafting a new selection of study tables. Meanwhile, our team can build a custom piece to your exact size and finish – just ask.",
        "seo_title": "Study Tables – Solid Wood Desks",
        "seo_description": "Study tables at SALAAR's HOME – solid wood desks with clean lines, arriving soon. Custom sizes available.",
        "order": 7,
        "is_in_header": False,
    },
]


class Command(BaseCommand):
    help = "Seeds categories, nav categories, and products from original data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding categories...")
        cat_map = {}
        for cdata in CATEGORIES_DATA:
            cat, _ = Category.objects.update_or_create(
                slug=cdata["slug"],
                defaults=cdata
            )
            cat_map[cdata["slug"]] = cat
        self.stdout.write(f"Categories seeded: {len(cat_map)}")

        self.stdout.write("Seeding nav categories...")
        for ndata in NAV_CATEGORIES_DATA:
            src = cat_map.get(ndata["source_slug"]) if ndata.get("source_slug") else None
            NavCategory.objects.update_or_create(
                slug=ndata["slug"],
                defaults={
                    "label": ndata["label"],
                    "source_category": src,
                    "tagline": ndata["tagline"],
                    "short": ndata["short"],
                    "description": ndata["description"],
                    "empty_title": ndata.get("empty_title", ""),
                    "empty_text": ndata.get("empty_text", ""),
                    "seo_title": ndata["seo_title"],
                    "seo_description": ndata["seo_description"],
                    "order": ndata["order"],
                    "is_in_header": ndata["is_in_header"],
                }
            )
        self.stdout.write("Nav categories seeded.")

        self.stdout.write("Seeding products from public/images-manifest.json...")
        try:
            with open("public/images-manifest.json", "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except Exception as e:
            self.stderr.write(f"Error loading manifest: {e}")
            return

        total_prod = 0
        for cat_slug, prod_list in manifest.get("products", {}).items():
            category = cat_map.get(cat_slug)
            if not category:
                continue

            for p in prod_list:
                tags = p.get("tags") or {}
                Product.objects.update_or_create(
                    slug=p["slug"],
                    defaults={
                        "item_id": p.get("id", p["slug"]),
                        "name": p["name"],
                        "category": category,
                        "price": p.get("price"),
                        "image": p["image"],
                        "gallery": p.get("gallery", []),
                        "description": p.get("description"),
                        "material": p.get("material", category.material),
                        "dimensions": p.get("dimensions", category.dimensions),
                        "color": p.get("color"),
                        "delivery_time": p.get("deliveryTime", category.delivery_time),
                        "availability": p.get("availability", "In Stock"),
                        "featured": bool(tags.get("featured", False)),
                        "best_selling": bool(tags.get("bestSelling", False)),
                        "is_new": bool(tags.get("isNew", False)),
                        "order": p.get("order", 0),
                    }
                )
                total_prod += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {total_prod} products into Django database."))
