from django.db import models
from django.contrib.auth.models import AbstractUser

class Category(models.Model):
    category_name = models.CharField(max_length=100, blank=True, null=True)
    category_image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    description = models.TextField(max_length=100, blank=True, null=True)

class Food(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="foods")
    food_name = models.CharField(max_length=150, blank=True, null=True)
    price = models.IntegerField(blank=True, null=True)
    food_image = models.ImageField(upload_to="foods/", blank=True, null=True)

    description = models.TextField(max_length=200, blank=True, null=True)
    AVAILABILITY_CHOICES = (
        ('Available', 'Available'),
        ('Out of Stock', 'Out of Stock'),
    )
    availability = models.CharField(
        max_length=20,
        choices=AVAILABILITY_CHOICES,
        default='Available'
    )

    prebook_only = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class AdminProfile(models.Model):
    user = models.OneToOneField(
        'UserApp.User',
        on_delete=models.CASCADE
    )
    role = models.CharField(max_length=50)