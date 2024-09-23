from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"), 
    path("wiki/<str:entry>", views.entry, name="entry"),
    path("random", views.random_entry, name="random"), 
    path("newpage", views.new_page, name="new"),
    path("edit/<str:entry>", views.edit, name="edit"),
    path("search", views.search, name="search"),
]
