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
        return self.paginate_posts(posts, page_number, request)

    @action(detail=False, methods=["get"])
    def following(self, request):
        """Holt nur die Posts von den gefolgten Usern"""
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        page_number = request.GET.get("page", 1)
        following_users = request.user.following.all()
        posts = Post.objects.filter(user__in=following_users).order_by("-time")
        return self.paginate_posts(posts, page_number, request)

    def paginate_posts(self, posts, page_number, request):
        """Hilfsmethode für die Pagination"""
        paginator = Paginator(posts, 10)
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
        return Response(response)




# @csrf_exempt
# def post(request):
#     if request.method == "POST" and request.user.is_authenticated:

#         # Get User and text of post
#         data = json.loads(request.body)
#         text = data.get('text')
#         if text == "":
#             return JsonResponse({
#                 "error": "Empty Post not allowed."
#             }, status=400)
#         user = request.user

#         # Save post to db
#         post = Post(
#             user=user,
#             text=text
#         )
#         post.save()
#         return JsonResponse({"message": "Posted successfully."}, status=201)
    
#     # Update text of post
#     elif request.method == "PUT" and request.user.is_authenticated:

#         # Get data
#         data = json.loads(request.body)
#         id = data.get('id')
#         try:
#             post = Post.objects.get(pk=id)
#         except Post.DoesNotExist:
#             return HttpResponse(status=404)

#         if data.get("liked") is not None:
#             u = request.user
#             exists = post.users_liked.filter(id=u.id).exists()
#             if data['liked'] and not exists:
#                 post.users_liked.add(request.user)
#             elif exists:
#                 post.users_liked.remove(request.user)
#             post.save()

        
#         # Save sended data
#         elif data.get("text") is not None:
#             # Handle invalid request
#             if request.user != post.user:
#                 return HttpResponse(status=403)
        
#             post.text = data["text"]
        
#         return HttpResponse(status=204)
        
#     # GET
#     else:
#         type = request.GET.get('type')
#         page_number = request.GET.get('page')
#         if type == 'all':
#             posts = Post.objects.order_by("-time").all()
#             paginator = Paginator(posts, 10)
#             page_obj = paginator.get_page(page_number)

#         elif type == 'following' and request.user.is_authenticated:
#             following_users = request.user.following.all()
#             posts = Post.objects.filter(user__in=following_users).order_by('-time')
#             paginator = Paginator(posts, 10)
#             page_obj = paginator.get_page(page_number)

#         posts = []
#         for post in page_obj:
#             posts.append({
#                 'post': post.serialize(), 
#                 'liked':  post.users_liked.filter(id=request.user.id).exists(),
#             })
        
#         response = {
#             'posts': posts,
#             'pagination': {
#                 'has_next': page_obj.has_next(),
#                 'has_previous': page_obj.has_previous(),
#                 'num_pages': list(page_obj.paginator.page_range),
#                 'current': page_obj.number,
#             },
#             'viewer': {
#                 'email': request.user.email if request.user.is_authenticated else '',
#                 'authenticated': request.user.is_authenticated,
#             },
#         }
#         return JsonResponse(response, safe=False)
        

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

        # Prepare posts
        posts = []
        for post in page_obj:
            posts.append({
                'post': post.serialize(), 
                'liked':  post.users_liked.filter(id=request.user.id).exists(),
            })
        
        return JsonResponse({
            'following': creator.following.count(),
            'followers': creator.followers.count(),
            'posts': posts,
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
