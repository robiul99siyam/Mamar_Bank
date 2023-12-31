from django.shortcuts import render, redirect
from django.views.generic import FormView, View, UpdateView
from django.contrib.auth import login, logout
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import EmailMultiAlternatives
# Create your views here.
from .forms import UserRegistrationForm, UpdateUser
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

class UserRegistrationView(FormView):
    template_name = "register.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, "LogIn Succfully !")
        login(self.request, user)
        subjetct_mail= 'Register Mamar Bank'
        message = render_to_string('sing.html',{
            'user':self.request.user
        })
        send_email = self.request.user.email
        send_email = EmailMultiAlternatives(subjetct_mail,'',to=[send_email])
        send_email.attach_alternative(message,'text/html')
        send_email.send()
        return super().form_valid(form)


class UserLogin(LoginView):
    template_name = "login.html"

    def get_success_url(self):
        messages.success(self.request, "LogIn Succfully !")
        return reverse_lazy("home")


class UserLogout(LogoutView):
    def get_success_url(self):
        messages.success(self.request, "Logout Succfully !")
        return reverse_lazy("home")


class UserUpdate(UpdateView):
    template_name = "profile.html"
    form_class = UpdateUser

    def get_success_url(self):
        messages.success(self.request, "You Data Update Succefully!")
        return reverse_lazy("profile")

    def get_object(self, queryset=None):
        return self.request.user


def password(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "password change successfully ")
            update_session_auth_hash(request, form.user)
            return redirect("home")
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, "password.html", {"form": form, "type": "Password change now "})