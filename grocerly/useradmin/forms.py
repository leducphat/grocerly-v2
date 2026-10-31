from core.models import Product, Vendor, Category
from django import forms
from django.utils.translation import gettext_lazy as _
from taggit.forms import TagField, TagWidget

class AddProductForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "Product Title", "class":"form-control"}))
    description = forms.CharField(widget=forms.Textarea(attrs={'placeholder': "Product Description", "class":"form-control"}))
    price = forms.CharField(widget=forms.NumberInput(attrs={'placeholder': "Sale Price", "class":"form-control", "step": "any"}))
    old_price = forms.CharField(widget=forms.NumberInput(attrs={'placeholder': "Old Price", "class":"form-control", "step": "any"}))
    stock_count = forms.CharField(widget=forms.NumberInput(attrs={'placeholder': "How many are in stock?", "class":"form-control"}))
    expiry_period = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "e.g., 6 months", 'class':'form-control'}), required=False)
    tags = TagField(widget=TagWidget(attrs={'placeholder': "Tags", "class":"form-control"}), required=False)
    image = forms.ImageField(widget=forms.FileInput(attrs={"class":"form-control"}), required=False)
    weight_volume = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "Volume/Weight (e.g. 1kg, 500ml)", "class":"form-control"}), required=False)
    ingredients = forms.CharField(widget=forms.Textarea(attrs={'placeholder': "Ingredients list", "class":"form-control"}), required=False)
    storage_instructions = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "e.g. Store in a cool dry place", "class":"form-control"}), required=False)
    # Required on purpose: the product cards link to these two, and an empty link
    # used to take the home page down for every customer (L-27, D-039).
    vendor = forms.ModelChoiceField(queryset=Vendor.objects.all(), widget=forms.Select(attrs={"class":"form-select select-nice"}), error_messages={"required": _("Please choose a vendor.")})
    category = forms.ModelChoiceField(queryset=Category.objects.all(), widget=forms.Select(attrs={"class":"form-select select-nice"}), error_messages={"required": _("Please choose a category.")})

    class Meta:
        model = Product
        fields = [
            'title',
            'image',
            'description',
            'price',
            'old_price',
            'specification',
            'stock_count',
            'expiry_period',
            'tags',
            'category',
            'weight_volume',
            'ingredients',
            'storage_instructions',
            'vendor',
        ]
