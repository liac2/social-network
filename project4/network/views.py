from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

from .models import User, Post
from .serializers import UserSerializer, PostSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import json


def index(request):
    return render(request, "network/index.html")


from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from django.core.paginator import Paginator
from .models import Post, User
from .serializers import PostSerializer, UserSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by("-time")
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        """Erstellt einen neuen Post"""
        text = request.data.get("text")
        if not text:
            return Response({"error": "Empty Post not allowed."}, status=status.HTTP_400_BAD_REQUEST)
        
        post = Post.objects.create(user=request.user, text=text)
        return Response({"message": "Posted successfully."}, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        """Bearbeitet den Post-Text oder das Like-System"""
        post = self.get_object()

        if "liked" in request.data:
            user = request.user
            if request.data["liked"]:
                post.users_liked.add(user)
            else:
                post.users_liked.remove(user)
            post.save()
            return Response({"message": "Like status updated."}, status=status.HTTP_204_NO_CONTENT)

        if "text" in request.data:
            if request.user != post.user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            post.text = request.data["text"]
            post.save()
            return Response({"message": "Post updated."}, status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def all(self, request):
        """Holt alle Posts mit Pagination"""
        page_number = request.GET.get("page", 1)
        posts = Post.objects.order_by("-time").all()
        return self.paginate_posts(posts, page_number, request, None)

    @action(detail=False, methods=["get"])
    def following(self, request):
        """Holt nur die Posts von den gefolgten Usern"""
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        page_number = request.GET.get("page", 1)
        following_users = request.user.following.all()
        posts = Post.objects.filter(user__in=following_users).order_by("-time")
        return self.paginate_posts(posts, page_number, request, None)

    @action(detail=True, methods=["get"], url_path="profile")
    def profile(self, request, pk=None):
        """Zeigt Profile page mit posts an"""

        page_number = request.GET.get("page", 1)

        try:
            post = Post.objects.get(pk=pk)  
            creator = post.user  
            posts = creator.posts.all()
            return self.paginate_posts(posts, page_number, request, creator)
        
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        
    @action(detail=True, methods=["patch"], url_path="profile/follow")
    def follow_profile(self, request, pk=None):
        """Follow / Unfollow profile"""

        try:
            post = Post.objects.get(pk=pk)  
            creator = post.user  
            viewer = request.user
        
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if 'following' in request.data:
            viewer.following.add(creator)
            viewer.save()
            return Response({"message": "Follow status updated."}, status=status.HTTP_204_NO_CONTENT)
        elif 'unfollow' in request.data:
            viewer.following.remove(creator)
            viewer.save()
            return Response({"message": "Follow status updated."}, status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def paginate_posts(self, posts, page_number, request, creator):
        """Hilfsmethode für die Pagination"""
        paginator = Paginator(posts, 5)
        page_obj = paginator.get_page(page_number)

        serialized_posts = [
            {
                "post": PostSerializer(post).data,
                "liked": post.users_liked.filter(id=request.user.id).exists() if request.user.is_authenticated else False
            }
            for post in page_obj
        ]

        response = {
            "posts": serialized_posts,
            "pagination": {
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
                "num_pages": list(page_obj.paginator.page_range),
                "current": page_obj.number,
            },
            "viewer": {
                "email": request.user.email if request.user.is_authenticated else "",
                "authenticated": request.user.is_authenticated,
            },
        }

        # Profile page
        if creator:
            viewer = request.user
            response['profile'] = {
                'following': creator.following.count(),
                'followers': creator.followers.count(),
                'email': creator.email,
                'followed_by_user': viewer.following.filter(id=creator.id).exists() if viewer.is_authenticated else ''
            }
        return Response(response)


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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
