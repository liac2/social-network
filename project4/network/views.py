from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

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
    
    # Update text of post
    elif request.method == "PUT" and request.user.is_authenticated:
        data = json.loads(request.body)
        id = data.get('id')
        post = Post.objects.get(pk=id)
        if request.user != post.user:
            return HttpResponse(status=403)
        text = data.get('text')
        post.text = text
        post.save()
        return HttpResponse(status=204)
        
    else:
        type = request.GET.get('type')
        page_number = request.GET.get('page')
        if type == 'all':
            posts = Post.objects.order_by("-time").all()
            paginator = Paginator(posts, 10)
            page_obj = paginator.get_page(page_number)

        elif type == 'following' and request.user.is_authenticated:
            following_users = request.user.following.all()
            posts = Post.objects.filter(user__in=following_users).order_by('-time')
            paginator = Paginator(posts, 10)
            page_obj = paginator.get_page(page_number)
        
        response = {
            'posts': [post.serialize() for post in page_obj],
            'pagination': {
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'num_pages': list(page_obj.paginator.page_range),
                'current': page_obj.number,
            },
            'viewer': {
                'email': request.user.email if request.user.is_authenticated else '',
                'authenticated': request.user.is_authenticated,
            },
        }
        return JsonResponse(response, safe=False)
        

@csrf_exempt
def profile(request):

    # Return profile page
    if request.method == "GET":
        id = request.GET.get('id')
        page_number = request.GET.get('page')
        creator = Post.objects.get(pk=id).user
        posts = creator.posts.order_by("-time").all()
        paginator = Paginator(posts, 10)
        page_obj = paginator.get_page(page_number)
        viewer = request.user
        
        return JsonResponse({
            'following': creator.following.count(),
            'followers': creator.followers.count(),
            'posts': [post.serialize() for post in page_obj],
            'pagination': {
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'num_pages': list(page_obj.paginator.page_range),
                'current': page_obj.number,
            },
            'email': creator.email,
            'viewer': {
                'email': request.user.email if viewer.is_authenticated else '',
                'authenticated': viewer.is_authenticated,
                'following': creator in viewer.following.all() if viewer.is_authenticated else ''
            }
        })

    # Update whether user follows or unfollows
    elif request.method == "PUT":
        id = request.GET.get('id')
        creator = Post.objects.get(pk=id).user
        viewer = request.user
        data = json.loads(request.body)

        # Follow
        if data.get("following"):
            viewer.following.add(creator)

        # Unfollow
        else:
            viewer.following.remove(creator)
            
        viewer.save()
        return HttpResponse(status=204)

    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)


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
