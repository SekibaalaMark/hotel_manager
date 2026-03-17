from django.urls import path
from .views import *

urlpatterns = [
    path("create/", CreateBookingView.as_view()),
    path("invoice/<int:booking_id>/", BookingInvoiceView.as_view()),
]