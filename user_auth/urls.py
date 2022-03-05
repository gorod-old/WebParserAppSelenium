from django.urls import path

from user_auth.views import *

urlpatterns = [
    path('login', entry, name='login'),
    path('user-auth/', user_auth, name='user-auth'),
    path('user-signup/', create_user, name='user-signup'),
    path('user-logout/', user_logout, name='user-logout'),
    path('activate/', activate_user, name='activate'),
]
