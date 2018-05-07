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
    name = models.CharField(max_length=100, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Listing(models.Model):

    host = models.ForeignKey(User, related_name = 'has_listings', on_delete=models.CASCADE)
    desc = models.TextField(blank=True)
    bedroom = models.IntegerField()
    bath = models.IntegerField()
    bed = models.IntegerField()
    num_guests = models.IntegerField()

    address = models.TextField(blank=True)
    
    amenities = models.ManyToManyField(Amenity, blank=True)

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



