from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import formats


class User(AbstractUser):
    watchlist = models.ManyToManyField('Listing', related_name='watchers', blank=True)
    bids_placed = models.ManyToManyField('Bid', related_name='bidders', blank=True)
    listings_placed = models.ManyToManyField('Listing', related_name='seller_listings', blank=True)

    def __str__(self):
        return self.username

class Category(models.Model):
    category = models.CharField(max_length=20)

    def __str__(self):
        return self.category

class Listing(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=500)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    picture = models.URLField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seller", blank=True, null=True, default=None)
    highest_bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="buyer", blank=True, null=True, default=None)

    def __str__(self):
        return f"{self.title} ({self.price}): {self.description}"

class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bid on '{self.listing.title}' by {self.bidder.username}: {self.amount}"


class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment on '{self.listing.title}' by {self.commenter.username}: {self.content}"
