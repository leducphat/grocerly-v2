from django import forms
from core.models import CartOrder, ProductReview
from userauths.models import ContactUs


class ProductReviewForm(forms.ModelForm):
    review = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Write your review'}))

    class Meta:
        model = ProductReview
        fields = ['review', 'rating']


def column_length(model, field):
    """The max_length of a model column, so a form box never allows more than the
    database stores (L-50, D-055)."""
    return model._meta.get_field(field).max_length


class ContactForm(forms.ModelForm):
    """The contact form (UC-08, L-50). Name, email and message are required; phone
    and subject may stay empty. Each length comes from the ContactUs column."""

    email = forms.EmailField(max_length=column_length(ContactUs, "email"))

    class Meta:
        model = ContactUs
        fields = ["full_name", "email", "phone", "subject", "message"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["phone"].required = False
        self.fields["subject"].required = False


class CheckoutInfoForm(forms.Form):
    """The shipping information of an order (UC-09, L-50). Full name, email and
    address are required, as before; each length comes from the CartOrder column.
    The box of the phone number is called `mobile` on the page."""

    full_name = forms.CharField(max_length=column_length(CartOrder, "full_name"))
    email = forms.EmailField(max_length=column_length(CartOrder, "email"))
    mobile = forms.CharField(max_length=column_length(CartOrder, "phone"), required=False)
    address = forms.CharField(max_length=column_length(CartOrder, "address"))
    city = forms.CharField(max_length=column_length(CartOrder, "city"), required=False)
    state = forms.CharField(max_length=column_length(CartOrder, "state"), required=False)
    country = forms.CharField(max_length=column_length(CartOrder, "country"), required=False)
