from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


class LoginSerializer(serializers.Serializer):

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):

        username = data.get("username")
        password = data.get("password")

        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError("Invalid username or password")

        if not user.is_active and not user.is_superuser:
            raise serializers.ValidationError("User account is disabled")

        refresh = RefreshToken.for_user(user)

        role = None

        if user.groups.exists():
            role = user.groups.first().name

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user_id": user.id,
            "username": user.username,
            "role": role,
            "must_change_password": user.must_change_password
        }



from rest_framework import serializers
from django.contrib.auth.models import Group
from .models import CustomUser


class GuestRegistrationSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ["id","username","email","phone","password","confirm_password"]

    def create(self, validated_data):
        validated_data.pop("confirm_password")

        password = validated_data.pop("password")

        user = CustomUser(**validated_data)
        user.set_password(password)

        user.save()

        guest_group = Group.objects.get(name="Guest")
        user.groups.add(guest_group)

        return user
    





class StaffCreateSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "phone",
            "password"
        ]

    def create(self, validated_data):

        password = validated_data.pop("password")

        user = CustomUser(**validated_data)
        user.set_password(password)

        user.must_change_password = True

        user.save()

        return user
    

    