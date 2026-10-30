import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def send_welcome_signup_email(user):
    """
    Sends a warm, luxury welcome email to newly registered clients on SALAAR's HOME.
    """
    recipient_email = (user.email or "").strip()
    if not recipient_email:
        logger.info(f"User {user.username} has no email address; skipping welcome email.")
        return False

    first_name = (user.first_name or "").strip()
    full_name = f"{first_name} {user.last_name or ''}".strip() or user.username

    site_info = {
        "name": getattr(settings, "SITE_NAME", "SALAAR's HOME"),
        "url": getattr(settings, "SITE_URL", "https://salaars-home-omega.vercel.app").rstrip("/"),
        "phone_display": getattr(settings, "SITE_PHONE_DISPLAY", "+91 98000 00000"),
        "phone_intl": getattr(settings, "SITE_PHONE_INTL", "919800000000"),
        "address": getattr(settings, "SITE_ADDRESS", "Furniture Showroom, Kirti Nagar, New Delhi, India"),
        "hours": getattr(settings, "SITE_HOURS", "Every day · 8:00 AM – 9:00 PM"),
    }

    context = {
        "user": user,
        "first_name": first_name or user.username,
        "full_name": full_name,
        "site": site_info,
    }

    subject = f"Welcome to SALAAR's HOME Furniture – Delhi Showroom"
    html_content = render_to_string("emails/welcome_signup.html", context)
    text_content = render_to_string("emails/welcome_signup.txt", context)

    from_email = settings.DEFAULT_FROM_EMAIL

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[recipient_email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        logger.info(f"Successfully sent welcome signup email to {recipient_email}")
        return True
    except Exception as exc:
        logger.error(f"Failed to send welcome signup email to {recipient_email}: {exc}")
        return False


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
        "phone_display": getattr(settings, "SITE_PHONE_DISPLAY", "+91 98000 00000"),
        "phone_intl": getattr(settings, "SITE_PHONE_INTL", "919800000000"),
        "address": getattr(settings, "SITE_ADDRESS", "Furniture Showroom, Kirti Nagar, New Delhi, India"),
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

    from_email = settings.DEFAULT_FROM_EMAIL

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

