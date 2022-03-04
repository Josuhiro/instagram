from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .forms import PostForm
from .models import *


# Create your views here.

@login_required
def index(request):
    user = request.user
    posts = Stream.objects.filter(user=user)
    group_ids = []
    for post in posts:
        group_ids.append(post.post_id)
    post_items = Post.objects.filter(id__in=group_ids).all().order_by('-posted')
    context = {'post_items': post_items}
    return render(request, 'index.html', context)


@login_required
def newPost(request):
    user = request.user.id
    tags_objs = []
    form = PostForm()

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            picture = form.cleaned_data.get("picture")
            caption = form.cleaned_data.get("caption")
            tags_form = form.cleaned_data.get("tags")

            tags_list = list(tags_form.split(','))

            for tag in tags_list:
                t, created = Tag.objects.get_or_create(title=tag)
                tags_objs.append(t)
            p, created = Post.objects.get_or_create(picture=picture, caption=caption, user_id=user)
            p.tags.set(tags_objs)
            p.save()
            return redirect('index')
    context = {'form': form}
    return render(request, 'new_post.html', context)


@login_required
def postDetails(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    context = {'post': post}

    return render(request, 'post_detail.html', context)


@login_required
def tags(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = Post.objects.filter(tags=tag).order_by('-posted')
    context = {'tag': tag, 'posts': posts}

    return render(request, 'tag.html', context)
