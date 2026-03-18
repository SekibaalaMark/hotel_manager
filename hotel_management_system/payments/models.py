from django.db import models

class Payment(models.Model):

    METHODS = [
        ("cash", "Cash"),
        ("card", "Card"),
        ("mobile_money", "Mobile Money")
    ]

    booking = models.OneToOneField(
        'bookings.Booking',
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    payment_method = models.CharField(max_length=20, choices=METHODS)

    paid_at = models.DateTimeField(auto_now_add=True)

    successful = models.BooleanField(default=True)