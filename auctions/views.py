from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Bid, Category, Comment
from .forms import ListingForm, BidForm

def index(request):
    listings = Listing.objects.filter(active=True)

    return render(request, "auctions/index.html",{
        "listings": listings
    })

def categories(request, category):
    all_categories = Category.objects.all()
    if category=='all':
        listings = Listing.objects.filter(active=True)
    else:
        category_choice = Category.objects.get(category=category)
        listings = Listing.objects.filter(category=category_choice, active=True)

    context = {
        "category": category,
        "all_categories": all_categories,
        "listings": listings
    }

    if not listings.exists():
        context["no_listings"] = True

    return render(request, "auctions/categories.html", context)

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))

        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })

    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)

    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })

        login(request, user)
        return HttpResponseRedirect(reverse("index"))

    else:
        return render(request, "auctions/register.html")

def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    comments = Comment.objects.filter(listing=listing)
    bid_count = listing.bids.count()

    return render(request, "auctions/listing.html",{
        "listing": listing,
        "bid_count": bid_count,
        "comments": comments
    })

@login_required
def create_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST)

        if form.is_valid():
            listing = form.save(commit=False)
            listing.seller = request.user
            listing.save()
            return HttpResponseRedirect((reverse('index')))

    else:
        form = ListingForm()

    return render(request, "auctions/create_listing.html", {
        'form': form
    })

@login_required
def close_auction(request, listing_id):
    if request.method == 'POST':
        listing = Listing.objects.get(pk=listing_id)
        listing.active = False
        listing.save()

    return HttpResponseRedirect((reverse('index')))

@login_required
def bid(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)

    if request.method == 'POST':
        form = BidForm(request.POST)

        if form.is_valid():
            bid_amount = form.cleaned_data['amount']

            if bid_amount > listing.price:
                # Create bid object
                bid = Bid(listing=listing, bidder=request.user, amount=bid_amount)
                bid.save()

                # Update listing price
                listing.price = bid_amount
                listing.highest_bidder = request.user
                listing.save()

                return HttpResponseRedirect(reverse("listing", args=[listing_id]))
            else:
                return render(request, "auctions/listing.html",{
                    "listing": listing,
                    "form": form,
                    "error": f"Bid must be higher than current price of ${listing.price:,}"
                })

    else:
        form = BidForm()

    return render(request, "auctions/listing.html",{
        "listing": listing,
        "form": form
    })

@login_required
def toggle_watchlist(request, listing_id):
    if request.method == 'POST':
        listing = Listing.objects.get(pk=listing_id)
        user = request.user

        # Removes from watchlist if already on watchlist
        if listing in user.watchlist.all():
            user.watchlist.remove(listing)
        # Adds to watchlist otherwise
        else:
            user.watchlist.add(listing) 

    return HttpResponseRedirect(reverse('listing', args=[listing_id]))

@login_required
def watchlist(request):
    user = request.user
    watchlist = user.watchlist.all()

    return render(request, "auctions/index.html",{
        "listings": watchlist
    })

@login_required
def add_comment(request, listing_id):
    if request.method == 'POST':
        listing = Listing.objects.get(pk=listing_id)
        content = request.POST.get('content')
        Comment.objects.create(listing=listing, commenter=request.user, content=content)

    return HttpResponseRedirect(reverse('listing', args=[listing_id]))
