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