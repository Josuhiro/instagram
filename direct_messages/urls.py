from django.urls import path
from .views import *


urlpatterns = [
    path('', inbox, name='inbox'),
    path('<username>', directs, name='directs'),
    path('wyslano/', send_direct, name='send_direct'),
    path('nowa/', user_search, name='user_search'),
    path('nowa/<username>', new_conversation, name='new_conversation'),

]
