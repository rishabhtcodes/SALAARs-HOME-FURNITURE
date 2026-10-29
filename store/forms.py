from django import forms
from django.contrib.auth.models import User
from .models import Order


class CheckoutForm(forms.ModelForm):
    payment_method = forms.ChoiceField(
        choices=Order.PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "sr-only"}),
        initial="card",
        required=False
    )

    class Meta:
        model = Order
        fields = ["full_name", "phone", "email", "address", "city", "payment_method", "notes"]
        widgets = {
            "full_name": forms.TextInput(attrs={
                "class": "w-full rounded-xl border border-line bg-linen px-4 py-3 text-sm text-ink placeholder:text-stone/60 focus:border-gold focus:outline-none",
                "placeholder": "Your Full Name",
                "required": True,
            }),
            "phone": forms.TextInput(attrs={
                "class": "w-full rounded-xl border border-line bg-linen px-4 py-3 text-sm text-ink placeholder:text-stone/60 focus:border-gold focus:outline-none",
                "placeholder": "e.g. 0300 1234567",
                "required": True,
            }),
            "email": forms.EmailInput(attrs={
                "class": "w-full rounded-xl border border-line bg-linen px-4 py-3 text-sm text-ink placeholder:text-stone/60 focus:border-gold focus:outline-none",
                "placeholder": "you@example.com (optional)",
            }),
            "city": forms.TextInput(attrs={
                "class": "w-full rounded-xl border border-line bg-linen px-4 py-3 text-sm text-ink placeholder:text-stone/60 focus:border-gold focus:outline-none",
                "placeholder": "Delhi",
                "required": True,
            }),
            "address": forms.Textarea(attrs={
                "class": "w-full rounded-xl border border-line bg-linen px-4 py-3 text-sm text-ink placeholder:text-stone/60 focus:border-gold focus:outline-none",
                "placeholder": "Street address, area, apartment / house number",
                "rows": 3,
                "required": True,
            }),
            "notes": forms.Textarea(attrs={
                "class": "w-full rounded-xl border border-line bg-linen px-4 py-3 text-sm text-ink placeholder:text-stone/60 focus:border-gold focus:outline-none",
                "placeholder": "Special delivery instructions, custom finish requests, etc.",
                "rows": 2,
            }),
        }


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "w-full rounded-xl border border-line bg-linen px-4 py-3 text-sm text-ink placeholder:text-stone/60 focus:border-gold focus:outline-none",
            "placeholder": "Create a password",
            "required": True,
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "w-full rounded-xl border border-line bg-linen px-4 py-3 text-sm text-ink placeholder:text-stone/60 focus:border-gold focus:outline-none",
            "placeholder": "Confirm password",
            "required": True,
        })
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]
        widgets = {
            "username": forms.TextInput(attrs={
                "class": "w-full rounded-xl border border-line bg-linen px-4 py-3 text-sm text-ink placeholder:text-stone/60 focus:border-gold focus:outline-none",
                "placeholder": "Username",
                "required": True,
            }),
            "email": forms.EmailInput(attrs={
                "class": "w-full rounded-xl border border-line bg-linen px-4 py-3 text-sm text-ink placeholder:text-stone/60 focus:border-gold focus:outline-none",
                "placeholder": "Email address",
                "required": True,
            }),
            "first_name": forms.TextInput(attrs={
                "class": "w-full rounded-xl border border-line bg-linen px-4 py-3 text-sm text-ink placeholder:text-stone/60 focus:border-gold focus:outline-none",
                "placeholder": "First name",
            }),
            "last_name": forms.TextInput(attrs={
                "class": "w-full rounded-xl border border-line bg-linen px-4 py-3 text-sm text-ink placeholder:text-stone/60 focus:border-gold focus:outline-none",
                "placeholder": "Last name",
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password")
        p2 = cleaned_data.get("confirm_password")
        if p1 and p2 and p1 != p2:
            self.add_error("confirm_password", "Passwords do not match.")
        return cleaned_data
