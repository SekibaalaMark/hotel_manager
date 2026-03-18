from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Room
from .serializers import *
from accounts.permissions import IsManager


class CreateRoomView(APIView):

    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):

        serializer = RoomSerializer(data=request.data)

        if serializer.is_valid():

            room = serializer.save()

            return Response(
                {
                    "message": "Room created successfully",
                    "room_number": room.number
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    




class BulkCreateRoomView(APIView):

    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):

        serializer = BulkRoomCreateSerializer(data=request.data)

        if serializer.is_valid():

            rooms = serializer.save()

            return Response(
                {
                    "message": "Rooms created successfully",
                    "rooms_created": len(rooms)
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    









from django.shortcuts import get_object_or_404

class UpdateRoomView(APIView):

    permission_classes = [IsAuthenticated, IsManager]

    def patch(self, request, room_id):

        room = get_object_or_404(Room, id=room_id)

        serializer = RoomUpdateSerializer(
            room,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():

            serializer.save()

            return Response(
                {
                    "message": "Room updated successfully",
                    "room": serializer.data
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Q

from .models import Room
from bookings.models import Booking
from .serializers import RoomListSerializer


class AvailableRoomsView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):

        check_in = request.query_params.get("check_in")
        check_out = request.query_params.get("check_out")

        if not check_in or not check_out:
            return Response(
                {"error": "check_in and check_out are required"},
                status=400
            )

        booked_rooms = Booking.objects.filter(
            Q(check_in__lt=check_out) &
            Q(check_out__gt=check_in)
        ).values_list("room_id", flat=True)

        rooms = Room.objects.exclude(id__in=booked_rooms)

        serializer = RoomListSerializer(rooms, many=True)

        return Response(serializer.data)