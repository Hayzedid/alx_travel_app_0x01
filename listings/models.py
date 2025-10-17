from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid


class Listing(models.Model):
    """
    Model for travel listings in the ALX Travel App.
    """
    title = models.CharField(max_length=200, help_text="Title of the travel listing")
    description = models.TextField(help_text="Detailed description of the listing")
    location = models.CharField(max_length=100, help_text="Location of the property")
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price per night in USD")
    max_guests = models.PositiveIntegerField(default=1, help_text="Maximum number of guests")
    bedrooms = models.PositiveIntegerField(default=1, help_text="Number of bedrooms")
    bathrooms = models.PositiveIntegerField(default=1, help_text="Number of bathrooms")
    amenities = models.JSONField(default=list, help_text="List of amenities available")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    # Foreign keys
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Travel Listing"
        verbose_name_plural = "Travel Listings"

    def __str__(self):
        return f"{self.title} - {self.location}"


class Booking(models.Model):
    """
    Model for booking reservations in the ALX Travel App.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    # Foreign keys
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bookings')
    guest = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    
    # Booking details
    check_in_date = models.DateField(help_text="Check-in date")
    check_out_date = models.DateField(help_text="Check-out date")
    number_of_guests = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Number of guests for this booking"
    )
    total_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Total price for the entire stay"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of the booking"
    )
    
    # Special requests
    special_requests = models.TextField(
        blank=True, 
        null=True, 
        help_text="Any special requests from the guest"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
        # Ensure no overlapping bookings for the same listing
        constraints = [
            models.CheckConstraint(
                check=models.Q(check_out_date__gt=models.F('check_in_date')),
                name='check_out_after_check_in'
            ),
        ]

    def __str__(self):
        return f"{self.guest.username} - {self.listing.title} ({self.check_in_date} to {self.check_out_date})"

    def clean(self):
        """Validate booking data"""
        from django.core.exceptions import ValidationError
        
        if self.check_out_date <= self.check_in_date:
            raise ValidationError("Check-out date must be after check-in date.")
        
        if self.number_of_guests > self.listing.max_guests:
            raise ValidationError(f"Number of guests ({self.number_of_guests}) exceeds maximum allowed ({self.listing.max_guests}).")

    def save(self, *args, **kwargs):
        """Override save to run clean validation"""
        self.clean()
        super().save(*args, **kwargs)


class Review(models.Model):
    """
    Model for reviews and ratings in the ALX Travel App.
    """
    # Foreign keys
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='reviews')
    guest = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    booking = models.OneToOneField(
        Booking, 
        on_delete=models.CASCADE, 
        related_name='review',
        help_text="The booking this review is for"
    )
    
    # Review content
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    title = models.CharField(max_length=200, help_text="Review title")
    comment = models.TextField(help_text="Detailed review comment")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether this review is verified (guest actually stayed)"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        # Ensure one review per booking
        unique_together = ['listing', 'guest', 'booking']

    def __str__(self):
        return f"{self.guest.username} - {self.listing.title} ({self.rating}/5 stars)"

    def clean(self):
        """Validate review data"""
        from django.core.exceptions import ValidationError
        
        if self.rating < 1 or self.rating > 5:
            raise ValidationError("Rating must be between 1 and 5.")
        
        # Ensure the booking belongs to the same listing and guest
        if self.booking.listing != self.listing:
            raise ValidationError("Booking must be for the same listing.")
        
        if self.booking.guest != self.guest:
            raise ValidationError("Booking must belong to the same guest.")

    def save(self, *args, **kwargs):
        """Override save to run clean validation"""
        self.clean()
        super().save(*args, **kwargs)


class Payment(models.Model):
    """
    Model for payment processing using Chapa API.
    """
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    # Foreign keys
    booking = models.OneToOneField(
        Booking, 
        on_delete=models.CASCADE, 
        related_name='payment',
        help_text="The booking this payment is for"
    )
    
    # Payment details
    payment_reference = models.CharField(
        max_length=100, 
        unique=True, 
        default=uuid.uuid4,
        help_text="Unique payment reference"
    )
    transaction_id = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="Chapa transaction ID"
    )
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Payment amount"
    )
    currency = models.CharField(
        max_length=3, 
        default='ETB',
        help_text="Payment currency (ETB for Ethiopian Birr)"
    )
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
        help_text="Current payment status"
    )
    
    # Chapa specific fields
    chapa_checkout_url = models.URLField(
        blank=True, 
        null=True,
        help_text="Chapa checkout URL for payment"
    )
    chapa_response = models.JSONField(
        default=dict,
        help_text="Full response from Chapa API"
    )
    
    # Customer details
    customer_email = models.EmailField(help_text="Customer email for payment")
    customer_phone = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        help_text="Customer phone number"
    )
    customer_name = models.CharField(
        max_length=100,
        help_text="Customer full name"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(
        blank=True, 
        null=True,
        help_text="When the payment was completed"
    )
    
    # Webhook and verification
    webhook_verified = models.BooleanField(
        default=False,
        help_text="Whether payment was verified via webhook"
    )
    verification_attempts = models.PositiveIntegerField(
        default=0,
        help_text="Number of verification attempts"
    )
    last_verification_at = models.DateTimeField(
        blank=True, 
        null=True,
        help_text="Last verification attempt timestamp"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self):
        return f"Payment {self.payment_reference} - {self.booking} ({self.status})"

    def mark_as_completed(self):
        """Mark payment as completed and update booking status"""
        self.status = 'completed'
        self.paid_at = timezone.now()
        self.save()
        
        # Update booking status to confirmed
        self.booking.status = 'confirmed'
        self.booking.save()

    def mark_as_failed(self, reason=None):
        """Mark payment as failed"""
        self.status = 'failed'
        if reason:
            self.chapa_response['failure_reason'] = reason
        self.save()

    @property
    def is_successful(self):
        """Check if payment is successful"""
        return self.status == 'completed'

    @property
    def can_be_refunded(self):
        """Check if payment can be refunded"""
        return self.status == 'completed' and self.paid_at

    def generate_new_reference(self):
        """Generate a new payment reference"""
        self.payment_reference = str(uuid.uuid4())
        self.save()
