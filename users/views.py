from django.shortcuts import render, redirect
from django.views.generic import View
from users.forms import CustomUserCreationForm
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse


class RegisterView(View):
    def get(self, request) -> HttpResponse:
        form = CustomUserCreationForm()
        return render(request, "users/register.html", {"form": form})

    def post(self, request) -> HttpResponse:
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Register suceed!")
            return redirect(reverse("task_index"))

        return render(request, "users/register.html", {"form": form})
