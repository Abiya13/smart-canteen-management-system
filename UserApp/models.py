from django.contrib.auth.models import AbstractUser
from django.db import models
from AdminApp.models import Food
from django.conf import settings
from datetime import date


# ⭐ Custom User Model
class User(AbstractUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# ⭐ Contact Model
class ContactDb(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    subject = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    message = models.TextField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name or "Contact Message"


class SaveCheckout(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    order_time = models.TimeField(null=True, blank=True)
    order_type = models.CharField(max_length=50, default="Instant")
    order_date = models.DateField(default=date.today)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)


# ⭐ Order (The Individual Items in a Checkout)
class Order(models.Model):
    # Links back to the Checkout/Transaction
    checkout = models.ForeignKey(SaveCheckout, on_delete=models.CASCADE, related_name='items', null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.food.food_name} (x{self.quantity})"


# ⭐ Cart Model
class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        # Ensure price is handled as a decimal for math consistency
        return self.food.price * self.quantity


class DiningBooking(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    date_time = models.DateTimeField()
    people = models.IntegerField(default=1)
    table_number = models.IntegerField(null=True, blank=True)
    special_request = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    def __str__(self):
        return f"Table for {self.name} on {self.date_time}"