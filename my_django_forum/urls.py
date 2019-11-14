"""my_django_forum URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url

from django.contrib.auth import views as auth_views
from registration import views as user_views
from chat import views as chat_views

from forum.views import ForumListView, SearchResultsView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', user_views.RegisterFormView.as_view(), name='register'),
    path('login/', auth_views.LoginView.as_view(template_name= 'registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logout.html'), name='logout'),
    path('profile/', user_views.ProfileFormView.as_view() , name='profile'),
    path('user_profile/<user>', user_views.UserProfileView.as_view(), name='user-profile'),
    path('password-reset/', user_views.UserPasswordResetView.as_view(), name='password_reset'),
    path('private-messages/', chat_views.PrivateMessagesListView.as_view(), name='private_messages'),
    
    path('password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),
        name='password_reset_confirm'),
    path('password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
        name='password_reset_done'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
        name='password_reset_complete'),
        path('register/', user_views.RegisterFormView.as_view(), name='register'),
    path('search/', SearchResultsView.as_view(), name='search-results'),
    path('', ForumListView.as_view(), name='home'),
    path('', include('forum.urls')),
    path('', include('chat.urls')),
    #path('', include('regististration.urls')),
]
