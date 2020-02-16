from django.urls import path

from accounts.views import LoginView, RegisterView, LogoutView

app_name    = 'accounts'
urlpatterns = [
    path('',LoginView.as_view(), name='login'),
    path('register/',RegisterView.as_view(), name='register'),
    path('logout/',LogoutView.as_view(), name='logout'),
]
