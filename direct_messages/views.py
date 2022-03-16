from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Message


@login_required
def inbox(request):
    user = request.user
    messages = Message.get_messages(user=user)
    active_direct = None
    directs = None

    if messages:
        message = messages[0]
        active_direct = message['user'].username
        directs = Message.objects.filter(user=user, recipient=message['user'])
        directs.update(is_read=True)

        for message in messages:
            if message['user'].username == active_direct:
                message['unread'] = 0

        context = {'messages': messages, 'active_direct': active_direct, 'directs': directs}

    return render(request, 'direct/direct.html', context)


@login_required
def directs(request, username):
    user = request.user
    messages = Message.get_messages(user=user)
    active_direct = username
    directs = Message.objects.filter(user=user, recipient__username=username)
    directs.update(is_read=True)

    for message in messages:
        if message['user'].username == username:
            message['unread'] = 0

    context = {'messages': messages, 'active_direct': active_direct, 'directs': directs}
    return render(request, 'direct/direct.html', context)


@login_required
def send_direct(request):
    from_user = request.user
    to_user_username = request.POST.get('to_user')
    content = request.POST.get('content')

    if request.method == "POST":
        to_user = User.objects.get(username=to_user_username)
        Message.send_message(from_user, to_user, content)
        return redirect('inbox')
    else:
        HttpResponseBadRequest()


@login_required
def user_search(request):
    query = request.GET.get('q')
    context = {}

    if query:
        users = User.objects.filter(Q(username__icontains=query))
        paginator = Paginator(users, 6)
        page_number = request.GET.get('page')
        users_paginator = paginator.get_page(page_number)
        context = {'users': users_paginator}

    return render(request, 'direct/search_user.html', context)


@login_required
def new_conversation(request, username):
    from_user = request.user
    content = ''
    try:
        to_user = User.objects.get(username=username)
    except Exception as e:
        return redirect('user_search')
    if from_user != to_user:
        Message.send_message(from_user, to_user, content)
    return redirect('inbox')


def check_directs(request):
    directs_count = 0
    if request.user.is_authenticated:
        directs_count = Message.objects.filter(user=request.user, is_read=False).count()

    return {'directs_count': directs_count}
