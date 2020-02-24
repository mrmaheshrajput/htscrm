from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.views.generic import View

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from accounts.forms import RegisterForm


class LoginView(View):
    template_name       = 'accounts/signin.html'

    def get(self, request):
        logout(request)
        return render(request, self.template_name)

    def post(self, request):
        email           = request.POST['email']
        password        = request.POST['password']
        user            = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('calls:call_register_view')
        else:
            return render(request, self.template_name, {'error': 'Email or password is incorrect'})


class RegisterView(View):
    template_name       = 'accounts/register.html'

    def get(self,request):
        return render(request, self.template_name)

    def post(self, request):
        form            = RegisterForm(request.POST)
        if form.is_valid():
            email       = request.POST['email']
            name        = request.POST['name']
            password    = request.POST['password']
            User.objects.create(
                username    = email,
                email       = email,
                first_name  = name,
                password    = make_password(password),
                is_superuser= 0,
            )
            print('User created successfully!')
            return redirect('accounts:login')
        else:
            return render(request, self.template_name, {'error': 'Invalid details submitted'})


class LogoutView(View):

    def get(self, request):
        logout(request)
        return redirect('accounts:login')
