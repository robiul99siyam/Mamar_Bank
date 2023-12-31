from django.urls import path,include
from . import views
urlpatterns = [
    path('register/' , views.UserRegistrationView.as_view(), name='register'),
    path('login/' , views.UserLogin.as_view(), name='login'),
    path('logout/' , views.UserLogout.as_view(), name='logout'),
    path('profile/' , views.UserUpdate.as_view(), name='profile'),
    path('password/', views.password,name='pass')
]
