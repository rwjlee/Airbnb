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

    host = models.ForeignKey(User, related_name = 'has_listings', null=True, on_delete=models.CASCADE)
    listing_type = models.TextField(max_length=50)
    privacy_type = models.TextField(max_length=10)
    bedroom = models.IntegerField()
    bath = models.IntegerField()
    bed = models.IntegerField()
    max_guests = models.IntegerField()
    city = models.TextField(max_length=100, blank=True)
    country = models.TextField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    amenities = models.ManyToManyField(Amenity)
    price = models.FloatField(null=True)
    active = models.BooleanField(default=False)
    
    name = models.TextField(max_length=200)
    desc = models.TextField(blank=True)

    addr_lat = models.FloatField(null=True)
    addr_lon = models.FloatField(null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Favorite(models.Model):
    guest = models.ForeignKey(User, related_name = 'likes', on_delete=models.CASCADE)
    home_listing = models.ForeignKey(Listing, related_name= 'saved_by', on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('guest', 'home_listing')

class Booking(models.Model):
    guest = models.ForeignKey(User, related_name = 'has_bookings', on_delete=models.CASCADE)
    home_listing = models.ForeignKey(Listing, related_name='has_guests', on_delete=models.CASCADE)
    charge_amount = models.FloatField(null=True)
    num_guests = models.IntegerField(null=True)
    
    from_date = models.DateField()
    to_date = models.DateField()

    is_cancelled = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Availability(models.Model):
    listing = models.ForeignKey(Listing, related_name = 'has_availability', on_delete=models.CASCADE)
    one_day = models.DateField(unique=False)
    available = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('listing', 'one_day')

class Review(models.Model):
    booking = models.ForeignKey(Booking, related_name = 'booking_reviewed', on_delete=models.CASCADE)
    description = models.CharField(max_length=500, default=None)
    star_rating = models.IntegerField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Conversation(models.Model):
    listing = models.ForeignKey(Listing, related_name= 'convo_about', on_delete=models.CASCADE)

    host = models.ForeignKey(User, related_name='host_conversations', on_delete=models.CASCADE)
    guest = models.ForeignKey(User, related_name='guest_conversations', on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Message(models.Model):
    contents = models.TextField(max_length=500)
    conversation = models.ForeignKey(Conversation, related_name= 'message_in_convo', on_delete=models.CASCADE)
    from_user = models.ForeignKey(User, related_name = 'messages', on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)