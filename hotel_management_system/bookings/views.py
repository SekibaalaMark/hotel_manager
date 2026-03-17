from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .serializers import BookingSerializer
from accounts.permissions import IsGuest


class CreateBookingView(APIView):

    permission_classes = [IsAuthenticated, IsGuest]

    def post(self, request):

        serializer = BookingSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():

            booking = serializer.save()

            return Response(
                {
                    "message": "Room booked successfully",
                    "booking_id": booking.id,
                    "status": booking.status
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    



# bookings/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Booking
from .serializers import BookingInvoiceSerializer


class BookingInvoiceView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, booking_id):

        booking = get_object_or_404(Booking, id=booking_id)

        serializer = BookingInvoiceSerializer(booking)

        return Response(serializer.data)