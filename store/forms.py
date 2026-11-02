from django import forms
from django.contrib.auth.models import User
from .models import Order, Product, Category


class ProductAdminForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "w-full rounded-xl border border-line bg-linen px-4 py-3 text-sm text-ink focus:border-gold focus:outline-none"})
    )
    new_category_name = forms.CharField(
        required=False,
        label="Or Create New Category",
        widget=forms.TextInput(attrs={"class": "w-full rounded-xl border border-line bg-linen px-4 py-3 text-sm text-ink placeholder:text-stone/60 focus:border-gold focus:outline-none", "placeholder": "e.g. Dining Tables / Study Desks"})
    )
    image_file = forms.ImageField(
        required=False,
        label="Upload New Image",
        widget=forms.FileInput(attrs={"class": "w-full rounded-xl border border-line bg-white px-4 py-3 text-sm text-ink focus:border-gold focus:outline-none"})
    )

    class Meta:
        model = Product
        fields = [
            "name",
            "category",
            "price",
            "image",
            "material",
            "dimensions",
            "color",
            "delivery_time",
            "availability",
            "stock",
            "description",
            "featured",
            "best_selling",
            "is_new",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "w-full rounded-xl border border-line bg-linen px-4 py-3 text-sm text-ink placeholder:text-stone/60 focus:border-gold focus:outline-none", "placeholder": "e.g. Royal Teak King Bed Set", "required": True}),
            "price": forms.NumberInput(attrs={"class": "w-full rounded-xl border border-line bg-linen px-4 py-3 text-sm text-ink placeholder:text-stone/60 focus:border-gold focus:outline-none", "placeholder": "120000", "required": True}),
            "image": forms.TextInput(attrs={"class": "w-full rounded-xl border border-line bg-linen px-4 py-3 text-sm text-ink placeholder:text-stone/60 focus:border-gold focus:outline-none", "placeholder": "/products/bedroom-sets/1.jpeg or paste image URL / data URL"}),
            "material": forms.TextInput(attrs={"class": "w-full rounded-xl border border-line bg-linen px-4 py-3 text-sm text-ink placeholder:text-stone/60 focus:border-gold focus:outline-none", "placeholder": "Solid Teak Wood / Sheesham"}),
            "dimensions": forms.TextInput(attrs={"class": "w-full rounded-xl border border-line bg-linen px-4 py-3 text-sm text-ink placeholder:text-stone/60 focus:border-gold focus:outline-none", "placeholder": "180x200 cm"}),
            "color": forms.TextInput(attrs={"class": "w-full rounded-xl border border-line bg-linen px-4 py-3 text-sm text-ink placeholder:text-stone/60 focus:border-gold focus:outline-none", "placeholder": "Warm Walnut"}),
            "delivery_time": forms.TextInput(attrs={"class": "w-full rounded-xl border border-line bg-linen px-4 py-3 text-sm text-ink placeholder:text-stone/60 focus:border-gold focus:outline-none", "placeholder": "7–15 days"}),
            "availability": forms.Select(attrs={"class": "w-full rounded-xl border border-line bg-linen px-4 py-3 text-sm text-ink focus:border-gold focus:outline-none"}),
            "stock": forms.NumberInput(attrs={"class": "w-full rounded-xl border border-line bg-linen px-4 py-3 text-sm text-ink focus:border-gold focus:outline-none", "placeholder": "10"}),
            "description": forms.Textarea(attrs={"class": "w-full rounded-xl border border-line bg-linen px-4 py-3 text-sm text-ink placeholder:text-stone/60 focus:border-gold focus:outline-none", "rows": 3, "placeholder": "Detailed product description..."}),
            "featured": forms.CheckboxInput(attrs={"class": "h-4 w-4 rounded border-line text-gold focus:ring-gold"}),
            "best_selling": forms.CheckboxInput(attrs={"class": "h-4 w-4 rounded border-line text-gold focus:ring-gold"}),
            "is_new": forms.CheckboxInput(attrs={"class": "h-4 w-4 rounded border-line text-gold focus:ring-gold"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get("category")
        new_category_name = (cleaned_data.get("new_category_name") or "").strip()
        if not category and not new_category_name:
            self.add_error("category", "Please select an existing category or enter a new category name.")
        return cleaned_data



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
                "placeholder": "e.g. 98765 43210",
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
            "autocomplete": "new-password",
            "required": True,
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "w-full rounded-xl border border-line bg-linen px-4 py-3 text-sm text-ink placeholder:text-stone/60 focus:border-gold focus:outline-none",
            "placeholder": "Confirm password",
            "autocomplete": "new-password",
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
                "autocomplete": "username",
                "required": True,
            }),
            "email": forms.EmailInput(attrs={
                "class": "w-full rounded-xl border border-line bg-linen px-4 py-3 text-sm text-ink placeholder:text-stone/60 focus:border-gold focus:outline-none",
                "placeholder": "Email address",
                "autocomplete": "email",
                "required": True,
            }),
            "first_name": forms.TextInput(attrs={
                "class": "w-full rounded-xl border border-line bg-linen px-4 py-3 text-sm text-ink placeholder:text-stone/60 focus:border-gold focus:outline-none",
                "placeholder": "First name",
                "autocomplete": "given-name",
            }),
            "last_name": forms.TextInput(attrs={
                "class": "w-full rounded-xl border border-line bg-linen px-4 py-3 text-sm text-ink placeholder:text-stone/60 focus:border-gold focus:outline-none",
                "placeholder": "Last name",
                "autocomplete": "family-name",
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password")
        p2 = cleaned_data.get("confirm_password")
        if p1 and p2 and p1 != p2:
            self.add_error("confirm_password", "Passwords do not match.")
        return cleaned_data
