from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import *
from .permissions import *



class LoginView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):

        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    





class GuestRegisterView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):

        serializer = GuestRegistrationSerializer(data=request.data)

        if serializer.is_valid():

            user = serializer.save()

            return Response(
                {
                    "message": "Guest registered successfully",
                    "username": user.username
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    







class CreateStaffUserView(APIView):

    permission_classes = [IsManager]

    def post(self, request):

        serializer = StaffCreateSerializer(data=request.data)

        if serializer.is_valid():

            user = serializer.save()

            staff_group = Group.objects.get(name="Staff")

            user.groups.add(staff_group)

            return Response(
                {
                    "message": "Staff user created successfully",
                    "username": user.username
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)