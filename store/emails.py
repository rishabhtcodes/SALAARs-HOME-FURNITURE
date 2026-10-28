import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def send_order_confirmation_email(order):
    """
    Sends a beautifully designed HTML & plain-text confirmation email
    to the customer if they provided an email address at checkout.
    """
    recipient_email = (order.email or "").strip()
    if not recipient_email and order.user and order.user.email:
        recipient_email = order.user.email.strip()

    if not recipient_email:
        logger.info(f"Order #{order.id} has no email associated; skipping email confirmation.")
        return False

    site_info = {
        "name": getattr(settings, "SITE_NAME", "SALAAR's HOME"),
        "url": getattr(settings, "SITE_URL", "https://salaars-home.vercel.app").rstrip("/"),
        "phone_display": getattr(settings, "SITE_PHONE_DISPLAY", "037 080 4453"),
        "phone_intl": getattr(settings, "SITE_PHONE_INTL", "92370804453"),
        "address": getattr(settings, "SITE_ADDRESS", "Furniture Showroom"),
        "hours": getattr(settings, "SITE_HOURS", "Every day · 8:00 AM – 9:00 PM"),
    }

    context = {
        "order": order,
        "items": order.items.all(),
        "site": site_info,
    }

    subject = f"Order #{order.id} Confirmed – SALAAR's HOME Furniture"
    html_content = render_to_string("emails/order_confirmation.html", context)
    text_content = render_to_string("emails/order_confirmation.txt", context)

    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "SALAAR's HOME <noreply@salaars-home.com>")

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[recipient_email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        logger.info(f"Successfully sent confirmation email for Order #{order.id} to {recipient_email}")
        return True
    except Exception as exc:
        logger.error(f"Failed to send confirmation email for Order #{order.id}: {exc}")
        return False

