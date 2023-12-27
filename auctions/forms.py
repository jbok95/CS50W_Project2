from django import forms
from .models import Listing, Bid

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = [
            'title',
            'description',
            'price',
            'picture',
            'category'
            ]

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = [
            'amount'
            ]
    amount = forms.DecimalField(label='Bid Amount', max_digits=10, decimal_places=2)
