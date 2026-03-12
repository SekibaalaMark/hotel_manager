from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Room
from .serializers import RoomSerializer
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