from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from decimal import Decimal

from accounts.models import CustomUser
from rooms.models import Room
from .models import Booking

class BookingModelTest(TestCase):

    def setUp(self):
        # 1. Create a Guest
        self.guest = CustomUser.objects.create_user(
            username="testguest", 
            password="password123"
        )

        # 2. Create a Room
        self.room = Room.objects.create(
            room_number="101",
            room_type="Deluxe",
            price_per_night=150.00
        )

        # 3. Define valid dates
        self.check_in = date.today()
        self.check_out = date.today() + timedelta(days=3)

    def test_booking_creation_and_defaults(self):
        """Test that a booking is created successfully with default values"""
        booking = Booking.objects.create(
            guest=self.guest,
            room=self.room,
            check_in=self.check_in,
            check_out=self.check_out,
            total_cost=450.00
        )

        self.assertEqual(booking.guest.username, "testguest")
        self.assertEqual(booking.room.room_number, "101")
        self.assertEqual(booking.status, "pending")  # Default value check
        self.assertEqual(booking.total_cost, Decimal("450.00"))
        self.assertIsNotNone(booking.created_at)

    def test_booking_status_choices(self):
        """Verify that the model enforces the STATUS choices"""
        booking = Booking(
            guest=self.guest,
            room=self.room,
            check_in=self.check_in,
            check_out=self.check_out,
            status="invalid_status_name"
        )
        
        # .full_clean() is required to trigger choice validation in a TestCase
        with self.assertRaises(ValidationError):
            booking.full_clean()

    def test_booking_on_delete_cascade(self):
        """Verify that deleting a user also deletes their bookings"""
        Booking.objects.create(
            guest=self.guest,
            room=self.room,
            check_in=self.check_in,
            check_out=self.check_out
        )
        
        self.guest.delete()
        self.assertEqual(Booking.objects.count(), 0)
        
        
        


from django.test import RequestFactory, TestCase
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from decimal import Decimal

from rooms.models import Room
from .serializers import BookingSerializer
from .models import Booking

User = get_user_model()

class BookingSerializerTest(TestCase):
    def setUp(self):
        # 1. Setup User and Room
        self.user = User.objects.create_user(username="traveller", password="password")
        self.room = Room.objects.create(
            room_number="202", 
            price_per_night=Decimal("100.00")
        )
        
        # 2. Mock a request with the user attached (needed for create() method)
        factory = RequestFactory()
        request = factory.post('/')
        request.user = self.user
        self.context = {'request': request}

        self.valid_data = {
            "room": self.room.id,
            "check_in": date.today(),
            "check_out": date.today() + timedelta(days=3)
        }

    def test_booking_calculation_logic(self):
        """Verify that total_cost is calculated correctly (100 * 3 days = 300)"""
        serializer = BookingSerializer(data=self.valid_data, context=self.context)
        
        self.assertTrue(serializer.is_valid(), serializer.errors)
        booking = serializer.save()

        # Calculation Check: (Check-out - Check-in) = 3 days. 3 * 100 = 300.
        self.assertEqual(booking.total_cost, Decimal("300.00"))
        self.assertEqual(booking.guest, self.user)

    def test_invalid_date_validation(self):
        """Verify that check_in after check_out raises a ValidationError"""
        invalid_data = self.valid_data.copy()
        invalid_data["check_in"] = date.today() + timedelta(days=5)
        invalid_data["check_out"] = date.today() + timedelta(days=2)

        serializer = BookingSerializer(data=invalid_data, context=self.context)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)
        self.assertEqual(serializer.errors["non_field_errors"][0], "Invalid dates")

    def test_read_only_fields(self):
        """Verify users cannot bypass pricing by sending their own total_cost"""
        data_with_price = self.valid_data.copy()
        data_with_price["total_cost"] = 1.00 # Attempting to pay only $1
        
        serializer = BookingSerializer(data=data_with_price, context=self.context)
        self.assertTrue(serializer.is_valid())
        booking = serializer.save()

        # Should ignore the 1.00 and calculate 300.00
        self.assertEqual(booking.total_cost, Decimal("300.00"))