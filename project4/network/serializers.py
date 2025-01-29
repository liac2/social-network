from rest_framework import serializers
from .models import User, Post


class UserSerializer(serializers.ModelSerializer):
    followers_count = serializers.IntegerField(source="followers.count", read_only=True)
    following_count = serializers.IntegerField(source="following.count", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "followers_count", "following_count"]

class PostSerializer(serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source="user.username")
    likes_count = serializers.IntegerField(source="users_liked.count", read_only=True)

    class Meta:
        model = Post
        fields = ["id", "creator", "text", "time", "likes_count"]
