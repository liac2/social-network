
# from django.urls import path

# from . import views

# urlpatterns = [
#     path("", views.index, name="index"),
#     path("login", views.login_view, name="login"),
#     path("logout", views.logout_view, name="logout"),
#     path("register", views.register, name="register"),
#     path("post", views.post, name="post"),
#     path("profile", views.profile, name="profile")
# ]


from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename="post")

urlpatterns = [
    path('api/', include(router.urls)),
]