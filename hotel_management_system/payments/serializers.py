from rest_framework import serializers
from .models import Payment
from bookings.models import Booking


from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = [
            "booking",
            "payment_method"
        ]

    def create(self, validated_data):

        booking = validated_data["booking"]

        payment = Payment.objects.create(
            booking=booking,
            amount=booking.total_cost,  # AUTO amount
            payment_method=validated_data["payment_method"]
        )

        # Auto confirm booking
        if payment.successful:
            booking.status = "confirmed"
            booking.save()

        return payment