from django import forms

from .models import Order


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("full_name", "email", "phone", "address", "postal_code", "city", "country")
        labels = {"full_name": "Full name", "postal_code": "Postal code"}
        widgets = {
            "full_name": forms.TextInput(attrs={"autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "phone": forms.TextInput(attrs={"autocomplete": "tel"}),
            "address": forms.TextInput(attrs={"autocomplete": "street-address"}),
            "postal_code": forms.TextInput(attrs={"autocomplete": "postal-code"}),
            "city": forms.TextInput(attrs={"autocomplete": "address-level2"}),
            "country": forms.TextInput(attrs={"autocomplete": "country-name"}),
        }
