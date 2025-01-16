from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

import json

from .models import User, Post

def index(request):
    return render(request, "network/index.html")

@csrf_exempt
def post(request):
    if request.method == "POST" and request.user.is_authenticated:

        # Get User and text of post
        data = json.loads(request.body)
        text = data.get('text')
        if text == "":
            return JsonResponse({
                "error": "Empty Post not allowed."
            }, status=400)
        user = request.user

        # Save post to db
        post = Post(
            user=user,
            text=text
        )
        post.save()
        return JsonResponse({"message": "Posted successfully."}, status=201)
    
    else:
        posts = Post.objects.order_by("-time").all()
        return JsonResponse([post.serialize() for post in posts], safe=False)

@csrf_exempt
def profile(request, id):
    creator = Post.objects.get(pk=id).user
    posts = creator.posts.order_by("-time").all()
    viewer = request.user
    
    return JsonResponse({
        'following': creator.following.count(),
        'followers': creator.followers.count(),
        'posts': [post.serialize() for post in posts],
        'email': creator.email,
        'viewer': {
            'email': request.user.email if viewer.is_authenticated else '',
            'authenticated': viewer.is_authenticated,
            'following': creator in viewer.following.all()
        }
    })


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
