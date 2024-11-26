from django.urls import path

from . import views

app_name = "wiki"
urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>", views.page, name="page"),
    path("wiki/", views.wiki, name="wiki"),             # wiki/ path without argument - only for using as url
    path("search/", views.search, name="search")
]
