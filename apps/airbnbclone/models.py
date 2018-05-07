from django.db import models

# Create your models here.

class User(models.Model):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=64)
    password = models.CharField(max_length=256)
    birthday = models.DateField(default=None, blank=True, null=True)
    gender = models.CharField(max_length=64, default=None, null=True)
    description = models.CharField(max_length=500, default=None, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Amenity(models.Model):
    name = models.CharField(max_length=50, unique=True)
    font_class = models.CharField(max_length=50, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Listing(models.Model):

    host = models.ForeignKey(User, related_name = 'has_listings', on_delete=models.CASCADE)
    listing_type = models.TextField(max_length=50)
    privacy_type = models.TextField(max_length=10)
    bedroom = models.IntegerField()
    bath = models.IntegerField()
    bed = models.IntegerField()
    num_guests = models.IntegerField()
    country = models.TextField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    amenities = models.ManyToManyField(Amenity, blank=True)
    
    name = models.TextField(max_length=200)
    desc = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Booking(models.Model):
    guest = models.ForeignKey(User, related_name = 'has_bookings', on_delete=models.CASCADE)
    home_listing = models.ForeignKey(Listing, related_name='has_guests', on_delete=models.CASCADE)
    charge_amount = models.FloatField()
    
    from_date = models.DateField()
    to_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Availability(models.Model):
    listing = models.ForeignKey(Listing, related_name = 'has_availability', on_delete=models.CASCADE)
    one_day = models.DateField()
    available = models.BooleanField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

