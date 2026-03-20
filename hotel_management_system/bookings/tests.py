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
        
        
        


from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from decimal import Decimal

from rooms.models import Room
from .models import Booking
from .serializers import BookingInvoiceSerializer

User = get_user_model()

class BookingInvoiceSerializerTest(TestCase):
    def setUp(self):
        # 1. Create dependencies
        self.user = User.objects.create_user(username="john_doe", password="password123")
        self.room = Room.objects.create(
            number="305-A", 
            price_per_night=Decimal("250.00")
        )
        
        # 2. Create the Booking object
        self.booking = Booking.objects.create(
            guest=self.user,
            room=self.room,
            check_in=date(2026, 5, 1),
            check_out=date(2026, 5, 5),
            total_cost=Decimal("1000.00"),
            status="confirmed"
        )

    def test_invoice_serialization_output(self):
        """Verify that the serializer correctly flattens related object data"""
        serializer = BookingInvoiceSerializer(instance=self.booking)
        data = serializer.data

        # Check flattened fields from the 'source' attribute
        self.assertEqual(data["guest_name"], "john_doe")
        self.assertEqual(data["room_number"], "305-A")
        self.assertEqual(Decimal(data["price_per_night"]), Decimal("250.00"))
        
        # Check direct model fields
        self.assertEqual(data["id"], self.booking.id)
        self.assertEqual(data["check_in"], "2026-05-01")
        self.assertEqual(data["status"], "confirmed")
        self.assertEqual(Decimal(data["total_cost"]), Decimal("1000.00"))

    def test_read_only_nature(self):
        """Verify that price_per_night and guest_name are present in the output"""
        serializer = BookingInvoiceSerializer(instance=self.booking)
        
        # Ensure the keys exist in the output
        expected_keys = {
            "id", "guest_name", "room_number", "check_in", 
            "check_out", "price_per_night", "total_cost", "status"
        }
        self.assertEqual(set(serializer.data.keys()), expected_keys)
        
        
        
        


from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import Group
from datetime import date, timedelta
from decimal import Decimal

from accounts.models import CustomUser
from rooms.models import Room
from .models import Booking

class CreateBookingViewTest(APITestCase):
    def setUp(self):
        # 1. Create the Guest group and a Guest user
        self.guest_group = Group.objects.create(name="Guest")
        self.guest_user = CustomUser.objects.create_user(
            username="guest_user", 
            password="password123"
        )
        self.guest_user.groups.add(self.guest_group)

        # 2. Create a Room (required for the serializer to calculate price)
        self.room = Room.objects.create(
            number="101", 
            price_per_night=Decimal("150.00")
        )

        # 3. Setup URLs and Payloads
        self.url = reverse('create-booking')  # Replace with your actual URL name
        self.valid_payload = {
            "room": self.room.id,
            "check_in": date.today(),
            "check_out": date.today() + timedelta(days=2)
        }

    def test_create_booking_success(self):
        """Test that an authenticated Guest can successfully book a room"""
        self.client.force_authenticate(user=self.guest_user)
        
        response = self.client.post(self.url, self.valid_payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "Room booked successfully")
        
        # Verify the booking exists in DB and total_cost was calculated (150 * 2)
        booking = Booking.objects.get(id=response.data["booking_id"])
        self.assertEqual(booking.total_cost, Decimal("300.00"))
        self.assertEqual(booking.guest, self.guest_user)

    def test_create_booking_unauthorized_user(self):
        """Test that a non-Guest user (e.g., Staff) is rejected by IsGuest"""
        staff_user = CustomUser.objects.create_user(username="staff", password="password")
        self.client.force_authenticate(user=staff_user)
        
        response = self.client.post(self.url, self.valid_payload, format='json')
        
        # Should be 403 Forbidden because of the IsGuest permission
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_booking_unauthenticated(self):
        """Test that unauthenticated requests are rejected"""
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_booking_invalid_dates(self):
        """Test validation error for check_in after check_out"""
        self.client.force_authenticate(user=self.guest_user)
        invalid_payload = self.valid_payload.copy()
        invalid_payload["check_in"] = date.today() + timedelta(days=5)
        invalid_payload["check_out"] = date.today() + timedelta(days=1)

        response = self.client.post(self.url, invalid_payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        
        
        
        






from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from decimal import Decimal

from rooms.models import Room
from .models import Booking

User = get_user_model()

class BookingInvoiceViewTest(APITestCase):
    def setUp(self):
        # 1. Setup two different users
        self.user = User.objects.create_user(username="customer1", password="password")
        self.other_user = User.objects.create_user(username="customer2", password="password")
        
        # 2. Setup a Room
        self.room = Room.objects.create(number="404", price_per_night=Decimal("200.00"))
        
        # 3. Create a Booking for the first user
        self.booking = Booking.objects.create(
            guest=self.user,
            room=self.room,
            check_in=date.today(),
            check_out=date.today() + timedelta(days=1),
            total_cost=Decimal("200.00"),
            status="confirmed"
        )
        
        # 4. Define URL (assuming path is 'invoice/<int:booking_id>/')
        self.url = reverse('booking-invoice', kwargs={'booking_id': self.booking.id})

    def test_get_invoice_success(self):
        """Verify that an authenticated user can retrieve their booking invoice"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify the flattened data from BookingInvoiceSerializer
        self.assertEqual(response.data["guest_name"], "customer1")
        self.assertEqual(response.data["room_number"], "404")
        self.assertEqual(Decimal(response.data["total_cost"]), Decimal("200.00"))

    def test_get_invoice_not_found(self):
        """Verify a 404 is returned for a non-existent booking ID"""
        self.client.force_authenticate(user=self.user)
        invalid_url = reverse('booking-invoice', kwargs={'booking_id': 9999})
        response = self.client.get(invalid_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_invoice_unauthenticated(self):
        """Verify unauthenticated users cannot access the invoice"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_privacy_logic(self):
        """
        Verify if the view restricts users from seeing other people's invoices.
        Note: Your current view logic doesn't restrict this yet, 
        so this test might fail until you update the view!
        """
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.url)
        
        # If you want privacy, this should ideally be 404 or 403.
        # Currently, your view will return 200 OK.
        # self.assertEqual(response.status_code, status.HTTP_