from rest_framework import serializers
from .models import Payment
from bookings.models import Booking


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = [
            "booking",
            "amount",
            "payment_method"
        ]

    def validate(self, data):

        booking = data["booking"]

        if booking.status != "pending":
            raise serializers.ValidationError(
                "Payment can only be made for pending bookings"
            )

        return data

    def create(self, validated_data):

        booking = validated_data["booking"]

        payment = Payment.objects.create(**validated_data)

        # Auto confirm booking after successful payment
        if payment.successful:
            booking.status = "confirmed"
            booking.save()

        return payment