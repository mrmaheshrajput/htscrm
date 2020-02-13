from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.views.generic import View

from django.contrib.auth import authenticate, login, logout


class LoginView(View):
    template_name       = 'accounts/signin.html'

    def get(self, request):
        return render(request, self.template_name)
