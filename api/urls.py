
from django.urls import path
from .views import *

urlpatterns = [
    path('login', Login.as_view(), name='user-login'),
    path('events', Linkfetch.as_view(), name='events'), 
    path('user/', Createuser.as_view(),name="create_user"),
    path('logout', Logout.as_view(), name='user-logout'),
    path('liked', Subscribeapi.as_view(), name='like-fetcher'),
    path('linkadd', Linkadd.as_view(), name='add-link'),
    path('verify/<auth_token>' , Verify.as_view() , name="verify"),
     
]
