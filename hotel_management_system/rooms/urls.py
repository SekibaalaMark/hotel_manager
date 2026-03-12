# rooms/urls.py
from django.urls import path
from .views import *

urlpatterns = [  # Must be exactly this name
    path("create/", CreateRoomView.as_view(), name="create-room"),
    path("bulk-create/", BulkCreateRoomView.as_view()),
]