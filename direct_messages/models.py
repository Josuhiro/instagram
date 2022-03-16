from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.db.models import Max


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='from_user')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='to_user')
    content = models.TextField(max_length=1000)
    date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def send_message(from_user, to_user, content):
        sender_message = Message(
            user=from_user,
            sender=from_user,
            recipient=to_user,
            content=content,
            is_read=True)
        sender_message.save()

        recipient_message = Message(
            user=to_user,
            sender=from_user,
            content=content,
            recipient=from_user,
        )
        recipient_message.save()
        return sender_message

    def get_messages(user):
        messages = Message.objects.filter(user=user).values('recipient').annotate(last=Max('date')).order_by('-last')
        users = []
        for message in messages:
            users.append({
                'user': User.objects.get(pk=message['recipient']),
                'last': message['last'],
                'unread': Message.objects.filter(user=user, recipient__pk=message['recipient'], is_read=False).count()
            })
        return users
