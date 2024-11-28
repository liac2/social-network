from django.urls import path

from . import views

app_name = "wiki"
urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>", views.page, name="page"),
    path("wiki/<str:title>/edit", views.edit, name="edit"),
    path("wiki/", views.wiki, name="wiki"),             # wiki/ path without argument - only for using as url
    path("search/", views.search, name="search"),
    path("new/", views.new, name="new")
]
