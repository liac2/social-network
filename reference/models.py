from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime 


class User(AbstractUser):
    watchlist = models.ManyToManyField("Listings", blank=True, related_name="users")


class Categories(models.Model):
    name = models.CharField(max_length=30)
    def __str__(self):
        return self.name


# auction listings
class Listings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_listings")
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=50)
    starting_bid = models.DecimalField(max_digits=5, decimal_places=2)
    url = models.URLField()
    # category = models.CharField(max_length=3, choices=categories, default="O", blank=True, null=True)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE, related_name="listings", null=True)
    start_date = models.DateField(default=datetime.date.today())
    end_date = models.DateField(default=datetime.date.min)
    active = models.BooleanField(default=True)


# bids
class Bids(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_bids")
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="bids")
    price = models.DecimalField(max_digits=5, decimal_places=2)


# comments made on auction listings
class Comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="comments")
    comment = models.CharField(max_length=100)
    date = models.DateField(default=datetime.date.today())
