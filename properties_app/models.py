from django.db import models
from django.contrib.auth.models import User

class Property(models.Model):
    BHK_CHOICES = [
        (1, '1 BHK'),
        (2, '2 BHK'),
        (3, '3 BHK'),
        (4, '4+ BHK'),
    ]

    PROPERTY_TYPE_CHOICES = [
        ('house', 'House'),
        ('apartment', 'Apartment'),
        ('plot', 'Plot'),
        ('commercial', 'Commercial'),
        ('pg', 'PG/Co-living'),
    ]

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('sold', 'Sold'),
        ('rented', 'Rented'),
    ]

    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES, default='house')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    survey_number = models.CharField(max_length=100, blank=True, null=True, help_text="Survey/Plot Number")
    free_vehicle_facility = models.BooleanField(default=False, help_text="Free vehicle facility for site visit")
    offers = models.CharField(max_length=255, blank=True, null=True, help_text="Special offers or discounts")
    
    # Amenities (Phase 2 Additions)
    has_parking = models.BooleanField(default=False)
    has_lift = models.BooleanField(default=False)
    has_power_backup = models.BooleanField(default=False)

    # Analytics / Popularity
    view_count = models.IntegerField(default=0, help_text="Number of times viewed")

    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2, help_text="Price in INR")
    bhk = models.IntegerField(choices=BHK_CHOICES, default=2)
    sqft = models.IntegerField(help_text="Area in Sq. Ft.")
    
    # Address details
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    
    # Map Coordinates
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Images
    image = models.ImageField(upload_to='property_images/', null=True, blank=True)
    virtual_tour_url = models.URLField(max_length=500, blank=True, null=True, help_text="Link to 360 Virtual Tour or Video")
    
    # Seller Details
    seller_name = models.CharField(max_length=150)
    seller_phone = models.CharField(max_length=20)
    seller_email = models.EmailField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.pk is not None:
            # Check if price changed
            orig = Property.objects.get(pk=self.pk)
            if orig.price != self.price:
                # Save the property first so that we don't have issues, but we can just create the history record.
                super().save(*args, **kwargs)
                self.price_history.create(
                    old_price=orig.price,
                    new_price=self.price,
                    reason="Automatic price update record"
                )
                return
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.city}"

class Facility(models.Model):
    property = models.ForeignKey(Property, related_name='facilities', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    distance_km = models.DecimalField(max_digits=4, decimal_places=2, help_text="Distance in KM")

    def __str__(self):
        return f"{self.name} near {self.property.title}"

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='property_gallery/')
    title = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.property.title}"

class PropertyVideo(models.Model):
    property = models.ForeignKey(Property, related_name='videos', on_delete=models.CASCADE)
    video = models.FileField(upload_to='property_videos/')
    title = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Video for {self.property.title}"

class PriceHistory(models.Model):
    property = models.ForeignKey(Property, related_name='price_history', on_delete=models.CASCADE)
    old_price = models.DecimalField(max_digits=12, decimal_places=2)
    new_price = models.DecimalField(max_digits=12, decimal_places=2)
    change_date = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.property.title} price changed to {self.new_price}"

class Wishlist(models.Model):
    user = models.ForeignKey(User, related_name='wishlist', on_delete=models.CASCADE)
    property = models.ForeignKey(Property, related_name='wishlisted_by', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'property')

    def __str__(self):
        return f"{self.user.username} - {self.property.title}"

class PropertyReview(models.Model):
    property = models.ForeignKey(Property, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], help_text="Rating from 1 to 5")
    review_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.property.title}"

class Inquiry(models.Model):
    property = models.ForeignKey(Property, related_name='inquiries', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='inquiries', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    message = models.TextField()
    inquiry_type = models.CharField(max_length=20, choices=[('email', 'Email'), ('whatsapp', 'WhatsApp')], default='email')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Inquiry by {self.name} for {self.property.title}"

class ChatMessage(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username}"
