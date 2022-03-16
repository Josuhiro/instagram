from django.urls import path
from .views import *


urlpatterns = [
    path('', show_notifications, name='show_notifications'),
    path('<noti_id>/usun', delete_notification, name='delete_notification'),


]
