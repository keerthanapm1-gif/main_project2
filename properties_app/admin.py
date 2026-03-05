from django.contrib import admin
from .models import Property, Facility, PropertyImage, PropertyVideo, PriceHistory, Wishlist, PropertyReview, Inquiry

class FacilityInline(admin.TabularInline):
    model = Facility
    extra = 1

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1

class PropertyVideoInline(admin.TabularInline):
    model = PropertyVideo
    extra = 1

class PriceHistoryInline(admin.TabularInline):
    model = PriceHistory
    extra = 0
    readonly_fields = ('change_date',)

class PropertyReviewInline(admin.TabularInline):
    model = PropertyReview
    extra = 0
    readonly_fields = ('created_at',)

class InquiryInline(admin.TabularInline):
    model = Inquiry
    extra = 0
    readonly_fields = ('created_at',)

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'property_type', 'status', 'city', 'price', 'bhk', 'sqft', 'seller_name')
    list_filter = ('property_type', 'status', 'city', 'bhk', 'state')
    search_fields = ('title', 'address', 'city', 'survey_number')
    inlines = [FacilityInline, PropertyImageInline, PropertyVideoInline, PriceHistoryInline, PropertyReviewInline, InquiryInline]

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'property', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'property__title')

@admin.register(PropertyReview)
class PropertyReviewAdmin(admin.ModelAdmin):
    list_display = ('property', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('property__title', 'user__username', 'review_text')

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'property', 'inquiry_type', 'created_at')
    list_filter = ('inquiry_type', 'created_at')
    search_fields = ('name', 'email', 'phone', 'property__title')

admin.site.register(Facility)
admin.site.register(PropertyImage)
admin.site.register(PropertyVideo)
admin.site.register(PriceHistory)
