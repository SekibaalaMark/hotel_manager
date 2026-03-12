from rest_framework import serializers
from .models import *


class RoomSerializer(serializers.ModelSerializer):

    class Meta:
        model = Room
        fields = [
            "id",
            "number",
            "room_type",
            "price_per_night",
            "is_available"
        ]
    
    def create(self, validated_data):
        room = Room(**validated_data)
        
        room.save()

        return room




class BulkRoomCreateSerializer(serializers.Serializer):

    start_room = serializers.IntegerField()
    end_room = serializers.IntegerField()
    room_type = serializers.ChoiceField(choices=Room.ROOM_TYPES)
    price_per_night = serializers.DecimalField(max_digits=8, decimal_places=2)

    def create(self, validated_data):

        start = validated_data["start_room"]
        end = validated_data["end_room"]
        room_type = validated_data["room_type"]
        price = validated_data["price_per_night"]

        rooms = []

        for number in range(start, end + 1):

            room, created = Room.objects.get_or_create(
                number=str(number),
                defaults={
                    "room_type": room_type,
                    "price_per_night": price
                }
            )

            if created:
                rooms.append(room)

        return rooms

