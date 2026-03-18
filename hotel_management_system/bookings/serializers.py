from rest_framework import serializers
from .models import Booking
from rooms.models import Room


class BookingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Booking
        fields = [
            "id",
            "room",
            "check_in",
            "check_out",
        ]

    def validate(self, data):

        room = data["room"]
        check_in = data["check_in"]
        check_out = data["check_out"]

        if check_in >= check_out:
            raise serializers.ValidationError(
                "Check-out date must be after check-in date"
            )

        # Prevent double booking
        booking_exists = Booking.objects.filter(
            room=room,
            check_in__lt=check_out,
            check_out__gt=check_in
        ).exists()

        if booking_exists:
            raise serializers.ValidationError(
                "This room is already booked for the selected dates"
            )

        return data

    def create(self, validated_data):

        user = self.context["request"].user

        booking = Booking.objects.create(
            guest=user,
            **validated_data
        )

        return booking