from django.db import models


class Room(models.Model):

    ROOM_TYPES = [
        ("single", "Single"),
        ("double", "Double"),
        ("suite", "Suite")
    ]

    number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2)

    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.number