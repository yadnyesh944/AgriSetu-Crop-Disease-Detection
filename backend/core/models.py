from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    role = models.CharField(
        max_length=10,
        choices=[
            ("FARMER", "Farmer"),
            ("GUIDE", "Agricultural Consultant"),
        ],
    )
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    full_name = models.CharField(max_length=120)
    location = models.CharField(max_length=150)
    contact_number = models.CharField(max_length=20)
    main_crop = models.CharField(max_length=100, blank=True)
    education = models.CharField(max_length=150, blank=True)
    qualification = models.CharField(max_length=200, blank=True)
    shop_name = models.CharField(max_length=150, blank=True)
    bank_name = models.CharField(max_length=120, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    ifsc = models.CharField(max_length=20, blank=True)
    points = models.PositiveIntegerField(default=0)


class Disease(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    crop = models.CharField(max_length=80)
    germination_date = models.DateField()
    soil = models.CharField(max_length=80)
    weather = models.CharField(max_length=80)
    image = models.ImageField(upload_to="disease/")
    prediction = models.CharField(max_length=150)
    confidence = models.FloatField()
    advice = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class SoilCheck(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=150)
    color = models.CharField(max_length=60)
    near_river = models.BooleanField()
    soil_image = models.ImageField(upload_to="soil/", blank=True)
    farm_image = models.ImageField(upload_to="farm/", blank=True)
    prediction = models.CharField(max_length=100)
    explanation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Connection(models.Model):
    farmer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="farmer_connections"
    )
    guide = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="guide_connections"
    )
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=10)
    status = models.CharField(max_length=20, default="PENDING")
    paid_at = models.DateTimeField(null=True, blank=True)


class Knowledge(models.Model):
    guide = models.ForeignKey(User, on_delete=models.CASCADE)
    crop = models.CharField(max_length=100)
    title = models.CharField(max_length=180)
    text = models.TextField()
    points = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(default=5)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
