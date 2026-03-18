from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .serializers import PaymentSerializer


class CreatePaymentView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = PaymentSerializer(data=request.data)

        if serializer.is_valid():

            payment = serializer.save()

            return Response(
                {
                    "message": "Payment successful",
                    "booking_status": payment.booking.status
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)