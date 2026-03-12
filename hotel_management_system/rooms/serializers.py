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

        

