from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Product

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # owner is set in the view, not by the user
        fields = ["name", "description", "price_tokens", "active"]
class BuyTokensForm(forms.Form):
    amount_tokens = forms.IntegerField(min_value=1, label="Amount of UPBolis")
    # Payment gateway goes here (Para el futuro pues dog)