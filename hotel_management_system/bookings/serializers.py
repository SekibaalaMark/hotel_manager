from rest_framework import serializers
from .models import Booking
from rooms.models import Room

from rest_framework import serializers
from .models import Booking
from datetime import timedelta


class BookingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Booking
        fields = [
            "id",
            "room",
            "check_in",
            "check_out",
            "total_cost"
        ]
        read_only_fields = ["total_cost"]

    def validate(self, data):

        if data["check_in"] >= data["check_out"]:
            raise serializers.ValidationError("Invalid dates")

        return data

    def create(self, validated_data):

        user = self.context["request"].user
        room = validated_data["room"]

        check_in = validated_data["check_in"]
        check_out = validated_data["check_out"]

        # Calculate number of days
        days = (check_out - check_in).days

        # Calculate total cost
        total_cost = room.price_per_night * days

        booking = Booking.objects.create(
            guest=user,
            total_cost=total_cost,
            **validated_data
        )

        return booking