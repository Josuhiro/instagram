from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from .views import *
urlpatterns = [
    path('', index, name='index'),
    path('dodaj_post/', newPost, name='newPost'),
    path('<uuid:post_id>', postDetails, name='postdetails'),
    path('tag/<slug:tag_slug>', tags, name='tags'),
    path('<uuid:post_id>/polubienie', like, name='like'),
    path('<uuid:post_id>/ulubione', favorite, name='favorite'),
]