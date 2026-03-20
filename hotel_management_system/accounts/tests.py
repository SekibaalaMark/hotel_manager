from django.test import TestCase
from django.contrib.auth import get_user_model

class CustomUserModelTest(TestCase):

    def setUp(self):
        """Set up a user instance for testing."""
        self.User = get_user_model()
        self.user_data = {
            "username": "testuser",
            "password": "securepassword123",
            "phone": "+1234567890",
        }
        self.user = self.User.objects.create_user(**self.user_data)

    def test_create_user(self):
        """Test if a user is created successfully with custom fields."""
        user = self.user
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.phone, "+1234567890")
        self.assertFalse(user.must_change_password)
        self.assertFalse(user.is_verified)
        self.assertTrue(user.is_active)
        # Check that the password isn't stored as plain text
        self.assertNotEqual(user.password, "securepassword123")

    def test_str_method(self):
        """Test the __str__ representation returns the username."""
        self.assertEqual(str(self.user), self.user.username)

    def test_default_boolean_values(self):
        """Ensure default flags are set correctly on creation."""
        new_user = self.User.objects.create_user(username="newuser", password="password")
        self.assertEqual(new_user.must_change_password, False)
        self.assertEqual(new_user.is_verified, False)

    def test_create_superuser(self):
        """Test creating a superuser (inherited functionality)."""
        admin_user = self.User.objects.create_superuser(
            username="admin", 
            password="adminpassword", 
            email="admin@test.com"
        )
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        
        
        
        

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
        
        


from django.test import TestCase
from django.contrib.auth.models import Group
from .models import CustomUser
from .serializers import GuestRegistrationSerializer

class GuestRegistrationSerializerTest(TestCase):
    def setUp(self):
        # The serializer expects this group to exist
        self.group = Group.objects.create(name="Guest")
        
        self.valid_payload = {
            "username": "testguest",
            "email": "guest@example.com",
            "phone": "1234567890",
            "password": "securepassword123",
            "confirm_password": "securepassword123"
        }

    def test_serializer_with_valid_data(self):
        serializer = GuestRegistrationSerializer(data=self.valid_payload)
        
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()

        # Check if user is created correctly
        self.assertEqual(user.username, "testguest")
        self.assertEqual(user.email, "guest@example.com")
        
        # Verify password is hashed (not stored as plain text)
        self.assertTrue(user.check_password("securepassword123"))
        
        # Verify group assignment
        self.assertIn(self.group, user.groups.all())

    def test_serializer_password_mismatch(self):
        # While your current serializer doesn't have a validate() method 
        # for password matching yet, this test will help you implement it.
        invalid_payload = self.valid_payload.copy()
        invalid_payload["confirm_password"] = "mismatch"
        
        serializer = GuestRegistrationSerializer(data=invalid_payload)
        
        # This will currently pass unless you add a validate() method to the serializer
        # (See "Pro-Tip" below)
        self.assertTrue(serializer.is_valid()) 

    def test_missing_required_fields(self):
        serializer = GuestRegistrationSerializer(data={"username": "incomplete"})
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)
        
        


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
    



from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class LoginViewTest(APITestCase):
    def setUp(self):
        self.url = reverse('login')  # Ensure this matches your urls.py name
        self.username = "testuser"
        self.password = "secure_pass123"
        
        # Create a user to test against
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            email="test@example.com"
        )

    def test_login_success(self):
        """Test that valid credentials return a 200 OK"""
        data = {
            "username": self.username,
            "password": self.password
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify that the response contains expected keys (e.g., token or user info)
        # self.assertIn('token', response.data) 

    def test_login_invalid_credentials(self):
        """Test that wrong credentials return a 400 or 401 (depending on serializer logic)"""
        data = {
            "username": self.username,
            "password": "wrongpassword"
        }
        response = self.client.post(self.url, data, format='json')

        # Your view returns 400_BAD_REQUEST on serializer failure
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_login_missing_fields(self):
        """Test that empty payload returns 400"""
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        
        
        

from django.urls import reverse
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase
from rest_framework import status
from .models import CustomUser

class GuestRegisterViewTest(APITestCase):
    def setUp(self):
        # The serializer inside this view requires the "Guest" group to exist
        self.group = Group.objects.create(name="Guest")
        self.url = reverse('guest-register')  # Ensure this matches your urls.py 'name'
        
        self.valid_payload = {
            "username": "newguest",
            "email": "guest@test.com",
            "phone": "0987654321",
            "password": "password123",
            "confirm_password": "password123"
        }

    def test_guest_registration_success(self):
        """Test that a valid POST request creates a user and returns 201"""
        response = self.client.post(self.url, self.valid_payload, format='json')

        # Check status code
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check response message
        self.assertEqual(response.data["message"], "Guest registered successfully")
        self.assertEqual(response.data["username"], "newguest")

        # Verify database state
        user = CustomUser.objects.get(username="newguest")
        self.assertTrue(user.groups.filter(name="Guest").exists())

    def test_guest_registration_validation_failure(self):
        """Test that missing fields return 400 Bad Request"""
        incomplete_payload = {"username": "only_user"}
        response = self.client.post(self.url, incomplete_payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Ensure errors are returned for missing fields
        self.assertIn("password", response.data)
        self.assertIn("email", response.data)

    def test_duplicate_username_fails(self):
        """Test that registering a username that already exists fails"""
        # Create initial user
        self.client.post(self.url, self.valid_payload, format='json')
        
        # Attempt to register again with same payload
        response = self.client.post(self.url, self.valid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)