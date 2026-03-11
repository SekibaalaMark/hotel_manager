from django.urls import path
from .views import *

urlpatterns = [
    path("register/", GuestRegisterView.as_view(), name="guest-register"),
    path("login/", LoginView.as_view(), name="login"),
]