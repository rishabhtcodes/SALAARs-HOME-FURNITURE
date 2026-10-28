from django.db import migrations

FAQ_DATA = [
    {
        "title": "Delivery Information",
        "items": [
            (
                "Do you deliver furniture to my area?",
                "Yes – we deliver nationwide with careful transport and professional assembly. Call us and we will confirm the delivery options and fee for your location.",
            ),
            (
                "How is my furniture delivered?",
                "Your furniture is wrapped and protected during transport, then moved into your home and assembled by our team. You do not have to lift a finger.",
            ),
            (
                "How much does delivery cost?",
                "The delivery fee depends on the distance and the size of the order. We always confirm the exact fee before you place your order – no surprises.",
            ),
        ],
    },
    {
        "title": "Custom Furniture",
        "items": [
            (
                "Can I order a custom size or finish?",
                "Absolutely. We regularly make custom pieces – different sizes, wood finishes, colors and materials. Share your measurements or a reference photo with us and we will quote you.",
            ),
            (
                "How do I order a custom piece?",
                "Simply call us or visit the showroom with your requirements (measurements, style, finish). We will confirm the design, materials and price before we start.",
            ),
            (
                "How long does a custom piece take?",
                "Custom furniture usually takes 7–20 days depending on the complexity of the design and our current production schedule.",
            ),
        ],
    },
    {
        "title": "Payment Methods",
        "items": [
            (
                "What payment methods do you accept?",
                "We accept cash and bank transfer. For custom-made and order-made items, a small deposit secures your order and the balance is paid upon delivery.",
            ),
            (
                "Do I need to pay the full amount in advance?",
                "No. For in-stock items you can pay on delivery. For made-to-order pieces we ask for a small deposit, with the balance due when your furniture arrives.",
            ),
            (
                "Do you offer installments?",
                "We can discuss flexible payment arrangements when you call – we will find a solution that works for you.",
            ),
        ],
    },
    {
        "title": "Contact Information",
        "items": [
            (
                "How can I reach SALAAR's HOME?",
                "The fastest way is a phone call at 037 080 4453. You can also message us on Facebook or TikTok – links are in the footer.",
            ),
            (
                "What are your opening hours?",
                "We are open every day from 8:00 AM to 9:00 PM. You are welcome to visit the showroom anytime during these hours.",
            ),
            (
                "Can I visit the showroom?",
                "Of course – we love showing our furniture in person. Visit us during opening hours, and for a smoother experience call us before you come.",
            ),
        ],
    },
    {
        "title": "Delivery Time",
        "items": [
            (
                "How long until I receive my furniture?",
                "In-stock pieces are typically delivered within 1–3 days. Made-to-order and custom pieces take around 7–20 days, depending on the design.",
            ),
            (
                "Can I choose a delivery date?",
                "Yes – when you place your order we will agree on a delivery day and time that suits you.",
            ),
        ],
    },
    {
        "title": "Warranty",
        "items": [
            (
                "Does my furniture come with a warranty?",
                "Yes. Our furniture is covered by a structural warranty, and our team stands behind the quality of every piece we sell.",
            ),
            (
                "What does the warranty cover?",
                "Manufacturing defects in the frame and structure are covered. If anything is wrong with the workmanship, we will repair or replace it free of charge.",
            ),
            (
                "What about after-sales care?",
                "We remain available after your purchase – for care advice, small repairs or guidance on keeping your wood furniture beautiful for years.",
            ),
        ],
    },
]


def seed_faq(apps, schema_editor):
    FAQGroup = apps.get_model("store", "FAQGroup")
    FAQItem = apps.get_model("store", "FAQItem")
    if FAQGroup.objects.exists():
        return
    for group_order, group in enumerate(FAQ_DATA):
        obj = FAQGroup.objects.create(title=group["title"], order=group_order)
        for item_order, (question, answer) in enumerate(group["items"]):
            FAQItem.objects.create(
                group=obj,
                question=question,
                answer=answer,
                order=item_order,
            )


def unseed_faq(apps, schema_editor):
    FAQGroup = apps.get_model("store", "FAQGroup")
    FAQGroup.objects.filter(title__in=[g["title"] for g in FAQ_DATA]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0002_faqgroup_faqitem"),
    ]

    operations = [
        migrations.RunPython(seed_faq, unseed_faq),
    ]
