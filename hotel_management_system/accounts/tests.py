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