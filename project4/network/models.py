from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime
from django.utils.timezone import now

class User(AbstractUser):
    pass

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    text = models.CharField(max_length=300)
    time = models.DateTimeField(auto_now_add=True)
    likes = models.PositiveIntegerField(default=0)
    
    def serialize(self):
        return {
            "id": self.id,
            "creator": self.user.username,
            "text": self.text,
            "time": self.time.strftime("%b %d %Y, %I:%M %p"),
            "likes": self.likes
        }