from django.contrib import admin
from .models import Listing, Booking, Review


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'location', 'price_per_night', 'max_guests', 'host', 'is_active', 'created_at']
    list_filter = ['is_active', 'location', 'created_at', 'bedrooms', 'bathrooms']
    search_fields = ['title', 'description', 'location', 'host__username']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_active']
    ordering = ['-created_at']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['guest', 'listing', 'check_in_date', 'check_out_date', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'created_at', 'check_in_date']
    search_fields = ['guest__username', 'listing__title', 'listing__location']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status']
    ordering = ['-created_at']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['guest', 'listing', 'rating', 'title', 'is_verified', 'created_at']
    list_filter = ['rating', 'is_verified', 'created_at']
    search_fields = ['guest__username', 'listing__title', 'title', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_verified']
    ordering = ['-created_at']
