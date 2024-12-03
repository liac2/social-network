from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

# auction listings
class listings(models.Model):
    pass

# bids
# comments made on auction listings
