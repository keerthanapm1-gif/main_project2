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
    floor_plan = models.ImageField(upload_to='floor_plans/', null=True, blank=True, help_text="Property Floor Plan")
    
    # Seller Details
    seller_name = models.CharField(max_length=150)
    seller_phone = models.CharField(max_length=20)
    seller_email = models.EmailField()

    # Agent Details
    agent_name = models.CharField(max_length=150, blank=True, null=True)
    agent_phone = models.CharField(max_length=20, blank=True, null=True)
    agent_email = models.EmailField(blank=True, null=True)

    # New Filters (Feature 3)
    FURNISHED_CHOICES = [
        ('unfurnished', 'Unfurnished'),
        ('semi-furnished', 'Semi-Furnished'),
        ('fully-furnished', 'Fully-furnished'),
    ]
    FACING_CHOICES = [
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West'),
        ('north-east', 'North-East'),
        ('north-west', 'North-West'),
        ('south-east', 'South-East'),
        ('south-west', 'South-West'),
    ]
    furnished_status = models.CharField(max_length=20, choices=FURNISHED_CHOICES, default='unfurnished')
    facing = models.CharField(max_length=20, choices=FACING_CHOICES, blank=True, null=True)
    floor_number = models.IntegerField(default=0, help_text="Floor number (0 for ground)")

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
    property = models.ForeignKey(Property, related_name='inquiries', on_delete=models.CASCADE, null=True, blank=True)
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

class Lease(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='leases')
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leases')
    start_date = models.DateField()
    end_date = models.DateField()
    rent_amount = models.DecimalField(max_digits=12, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=12, decimal_places=2)
    clauses = models.TextField(blank=True, null=True, help_text="Local legal clauses and terms")
    document = models.FileField(upload_to='leases/', blank=True, null=True)
    is_signed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Lease for {self.property.title} by {self.tenant.username}"

class PaymentSplit(models.Model):
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    is_deposit = models.BooleanField(default=False)
    
    # Split logic
    owner_split = models.DecimalField(max_digits=12, decimal_places=2)
    management_fee = models.DecimalField(max_digits=12, decimal_places=2)
    
    status_choices = [
        ('pending', 'Pending'),
        ('escrow', 'In Escrow'),
        ('released', 'Released to Owner')
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='escrow')

    def save(self, *args, **kwargs):
        if not self.is_deposit and self.management_fee == 0:
            # Assuming a standard 10% management fee for rent
            self.management_fee = float(self.amount_paid) * 0.10
            self.owner_split = float(self.amount_paid) - float(self.management_fee)
        elif self.is_deposit:
            # Deposits are fully held
            self.management_fee = 0
            self.owner_split = self.amount_paid
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment of {self.amount_paid} for {self.lease.property.title}"

class TaxReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tax_reports')
    year = models.IntegerField()
    report_type_choices = [
        ('1099', '1099-MISC'),
        ('expense', 'Expense Report')
    ]
    report_type = models.CharField(max_length=20, choices=report_type_choices)
    document = models.FileField(upload_to='tax_reports/', blank=True, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_report_type_display()} for {self.user.username} - {self.year}"

class SavedSearch(models.Model):
    user = models.ForeignKey(User, related_name='saved_searches', on_delete=models.CASCADE)
    query = models.CharField(max_length=200, blank=True, null=True, help_text="Search keyword")
    city = models.CharField(max_length=100, blank=True, null=True)
    property_type = models.CharField(max_length=20, blank=True, null=True)
    bhk = models.IntegerField(blank=True, null=True)
    min_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    max_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Saved search by {self.user.username}: {self.query or self.city or 'Custom filters'}"

    def get_search_url(self):
        params = []
        if self.query:
            params.append(f"q={self.query}")
        if self.property_type:
            params.append(f"type={self.property_type}")
        if self.bhk:
            params.append(f"bhk={self.bhk}")
        if self.min_price:
            params.append(f"min_price={int(self.min_price)}")
        if self.max_price:
            params.append(f"max_price={int(self.max_price)}")
        return "/properties/?" + "&".join(params) if params else "/properties/"

from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('agent', 'Agent'),
        ('user', 'User'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Ensure each user has a profile.
    Uses get_or_create to handles cases where existing users might not have a profile.
    """
    if created:
        UserProfile.objects.get_or_create(user=instance)
    else:
        # Use get_or_create to ensure the profile exists before saving
        profile, _ = UserProfile.objects.get_or_create(user=instance)
        profile.save()

class RecentlyViewed(models.Model):
    user = models.ForeignKey(User, related_name='recently_viewed', on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-viewed_at']
        unique_together = ('user', 'property')

    def __str__(self):
        return f"{self.user.username} viewed {self.property.title}"

