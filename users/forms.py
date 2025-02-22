from django.contrib.auth.forms import UserCreationForm
from users.models import CustomUser
from django.forms import forms


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = (
            "name",
            "email",
        )
