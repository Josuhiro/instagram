from django.db import models
from django.db.models.signals import post_save, post_delete

from notifications.models import Notification
from post.models import Post
from django.contrib.auth.models import User


# Create your models here.

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def user_commented_post(sender, instance, *args, **kwargs):
        comment = instance
        post = comment.post
        sender = comment.user
        text_preview = comment.content[:90]
        notify = Notification(post=post, sender=sender, user=post.user, text_preview=text_preview, notification_type=2)
        notify.save()

    def user_deleted_comment_post(sender, instance, *args, **kwargs):
        comment = instance
        post = comment.post
        sender = comment.user
        notify = Notification.objects.filter(post=post, sender=sender, user=post.user, notification_type=2)
        notify.delete()


post_save.connect(Comment.user_commented_post, sender=Comment)
post_delete.connect(Comment.user_deleted_comment_post, sender=Comment)
