from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import resolve

from authy.forms import SignupForm, ChangePasswordForm, EditProfileForm
from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash

from authy.models import Profile
from post.models import Post, Follow, Stream

from django.core.paginator import Paginator


# Create your views here.
def userProfile(request, username):
    user = get_object_or_404(User, username=username)
    profile = Profile.objects.get(user=user)
    url_name = resolve(request.path).url_name

    if url_name == 'profile':
        posts = Post.objects.filter(user=user).order_by('-posted')
    else:
        posts = profile.favorites.all()

    posts_count = Post.objects.filter(user=user).count
    following_count = Follow.objects.filter(follower=user).count
    followers_count = Follow.objects.filter(following=user).count

    follow_status = Follow.objects.filter(following=user, follower=request.user).exists()

    paginator = Paginator(posts, 8)
    page_number = request.GET.get('page')
    posts_paginator = paginator.get_page(page_number)

    context = {
        'posts': posts_paginator,
        'profile': profile,
        'url_name': url_name,
        'posts_count': posts_count,
        'following_count': following_count,
        'followers_count': followers_count,
        'follow_status': follow_status,
    }
    return render(request, 'profile.html', context)


def signup(request):
    form = SignupForm()
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            User.objects.create_user(username=username, email=email, password=password)
            return redirect('index')

    context = {'form': form}

    return render(request, 'signup.html', context)


@login_required
def passwordChange(request):
    user = request.user
    form = ChangePasswordForm(instance=user)
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data.get('new_password')
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            return redirect('change_password_done')

    context = {'form': form}

    return render(request, 'change_password.html', context)


def passwordChangeDone(request):
    return render(request, 'change_password_done.html')


@login_required
def editProfile(request):
    user = request.user.id
    profile = Profile.objects.get(user__id=user)
    form = EditProfileForm()

    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile.picture = form.cleaned_data.get('picture')
            profile.first_name = form.cleaned_data.get('first_name')
            profile.last_name = form.cleaned_data.get('last_name')
            profile.location = form.cleaned_data.get('location')
            profile.url = form.cleaned_data.get('url')
            profile.profile_info = form.cleaned_data.get('profile_info')
            profile.save()
            return redirect('index')

    context = {'form': form}

    return render(request, 'edit_profile.html', context)


@login_required
def follow(request, username, option):
    user = request.user
    following = get_object_or_404(User, username=username)

    try:
        f, created = Follow.objects.get_or_create(follower=user, following=following)
        if int(option) == 0:
            f.delete()
            Stream.objects.filter(following=following, user=user).all().delete()
        else:
            posts = Post.objects.all().filter(user=following)[:10]

            with transaction.atomic():
                for post in posts:
                    stream = Stream(post=post, user=user, date=post.posted, following=following)
                    stream.save()
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
    except User.DoesNotExist:
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
