from django.contrib.auth.forms import PasswordChangeForm
from core.models import Product, Vendor, Category
from django import forms
from django.utils.translation import gettext_lazy as _
from taggit.forms import TagField, TagWidget

from userauths.models import Profile

class AddProductForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'placeholder': _("Product name"), "class":"form-control"}))
    description = forms.CharField(widget=forms.Textarea(attrs={'placeholder': _("Product description"), "class":"form-control"}))
    # Number fields, not text, so a negative price or stock is refused (L-53, D-055).
    # max_digits and decimal_places are those of the columns in core.models.Product.
    price = forms.DecimalField(min_value=0, max_digits=20, decimal_places=2, widget=forms.NumberInput(attrs={'placeholder': _("Selling price"), "class":"form-control", "step": "any"}))
    old_price = forms.DecimalField(min_value=0, max_digits=20, decimal_places=2, widget=forms.NumberInput(attrs={'placeholder': _("Old price"), "class":"form-control", "step": "any"}))
    stock_count = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs={'placeholder': _("How many are in stock?"), "class":"form-control"}))
    expiry_period = forms.CharField(widget=forms.TextInput(attrs={'placeholder': _("e.g. 6 months"), 'class':'form-control'}), required=False)
    tags = TagField(widget=TagWidget(attrs={'placeholder': _("e.g. vegetables, organic"), "class":"form-control"}), required=False)
    image = forms.ImageField(widget=forms.FileInput(attrs={"class":"form-control"}), required=False)
    weight_volume = forms.CharField(widget=forms.TextInput(attrs={'placeholder': _("Weight or volume (e.g. 1kg, 500ml)"), "class":"form-control"}), required=False)
    ingredients = forms.CharField(widget=forms.Textarea(attrs={'placeholder': _("Ingredients"), "class":"form-control"}), required=False)
    # A field declared here does not take the model default, so the add page
    # starts the box with it; the staff changes it for fresh goods (L-71, D-063).
    storage_instructions = forms.CharField(widget=forms.TextInput(attrs={'placeholder': _("e.g. Store in a cool, dry place"), "class":"form-control"}), required=False,
                                           initial=Product._meta.get_field("storage_instructions").default)
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


class StaffProfileForm(forms.ModelForm):
    """The staff settings page (CN-32, L-45, L-50, D-055).

    A ModelForm checks the length of each box against its column, and an empty box
    is saved as empty (None), not as the word "None". The image box left empty keeps
    the photo the staff already has.
    """

    class Meta:
        model = Profile
        fields = ["full_name", "phone", "bio", "address", "country", "image"]
        widgets = {"image": forms.FileInput(attrs={"class": "form-control-file"})}


class StaffPasswordChangeForm(PasswordChangeForm):
    """Django's own change-password form, the one the customer's page uses (L-51):
    it checks the old password and runs AUTH_PASSWORD_VALIDATORS on the new one.
    Only the CSS class of the dashboard theme is added to its three boxes."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
