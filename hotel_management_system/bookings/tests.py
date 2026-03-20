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