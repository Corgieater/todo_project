from django.urls import path, include
from users.views import RegisterView

urlpatterns = [
    path("register", RegisterView.as_view(), name="register_page"),
    path("register", RegisterView.as_view(), name="register"),
    # path("", include("django.contrib.auth.urls")),
]
