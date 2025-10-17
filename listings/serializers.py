from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Listing, Booking, Review


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class ListingSerializer(serializers.ModelSerializer):
    """Serializer for Listing model with full CRUD operations"""
    host = UserSerializer(read_only=True)
    host_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'description', 'location', 'price_per_night',
            'max_guests', 'bedrooms', 'bathrooms', 'amenities',
            'created_at', 'updated_at', 'is_active', 'host', 'host_id'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Create a new listing"""
        # Set the host to the current user if not provided
        if 'host_id' not in validated_data:
            validated_data['host'] = self.context['request'].user
        else:
            host_id = validated_data.pop('host_id')
            validated_data['host_id'] = host_id
        
        return super().create(validated_data)
    
    def validate_price_per_night(self, value):
        """Validate price per night is positive"""
        if value <= 0:
            raise serializers.ValidationError("Price per night must be positive.")
        return value
    
    def validate_max_guests(self, value):
        """Validate max guests is at least 1"""
        if value < 1:
            raise serializers.ValidationError("Maximum guests must be at least 1.")
        return value


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for Booking model with full CRUD operations"""
    listing = ListingSerializer(read_only=True)
    listing_id = serializers.IntegerField(write_only=True)
    guest = UserSerializer(read_only=True)
    guest_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'listing', 'listing_id', 'guest', 'guest_id',
            'check_in_date', 'check_out_date', 'number_of_guests',
            'total_price', 'status', 'special_requests',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Create a new booking"""
        # Set the guest to the current user if not provided
        if 'guest_id' not in validated_data:
            validated_data['guest'] = self.context['request'].user
        else:
            guest_id = validated_data.pop('guest_id')
            validated_data['guest_id'] = guest_id
        
        return super().create(validated_data)
    
    def validate(self, data):
        """Validate booking data"""
        check_in = data.get('check_in_date')
        check_out = data.get('check_out_date')
        
        if check_in and check_out:
            if check_out <= check_in:
                raise serializers.ValidationError(
                    "Check-out date must be after check-in date."
                )
        
        # Validate number of guests against listing capacity
        listing_id = data.get('listing_id')
        number_of_guests = data.get('number_of_guests')
        
        if listing_id and number_of_guests:
            try:
                listing = Listing.objects.get(id=listing_id)
                if number_of_guests > listing.max_guests:
                    raise serializers.ValidationError(
                        f"Number of guests ({number_of_guests}) exceeds "
                        f"maximum allowed ({listing.max_guests})."
                    )
            except Listing.DoesNotExist:
                raise serializers.ValidationError("Invalid listing ID.")
        
        return data
    
    def validate_total_price(self, value):
        """Validate total price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Total price must be positive.")
        return value


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model"""
    listing = ListingSerializer(read_only=True)
    listing_id = serializers.IntegerField(write_only=True)
    guest = UserSerializer(read_only=True)
    guest_id = serializers.IntegerField(write_only=True, required=False)
    booking_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'listing', 'listing_id', 'guest', 'guest_id',
            'booking_id', 'rating', 'title', 'comment',
            'created_at', 'updated_at', 'is_verified'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_verified']
    
    def create(self, validated_data):
        """Create a new review"""
        # Set the guest to the current user if not provided
        if 'guest_id' not in validated_data:
            validated_data['guest'] = self.context['request'].user
        else:
            guest_id = validated_data.pop('guest_id')
            validated_data['guest_id'] = guest_id
        
        return super().create(validated_data)
    
    def validate_rating(self, value):
        """Validate rating is between 1 and 5"""
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
    
    def validate(self, data):
        """Validate review data"""
        booking_id = data.get('booking_id')
        listing_id = data.get('listing_id')
        
        if booking_id and listing_id:
            try:
                booking = Booking.objects.get(id=booking_id)
                if booking.listing.id != listing_id:
                    raise serializers.ValidationError(
                        "Booking must be for the same listing."
                    )
                
                # Check if user is the guest of the booking
                request_user = self.context['request'].user
                if booking.guest != request_user:
                    raise serializers.ValidationError(
                        "You can only review bookings you made."
                    )
                
            except Booking.DoesNotExist:
                raise serializers.ValidationError("Invalid booking ID.")
        
        return data


# Simplified serializers for list views
class ListingListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing list views"""
    host_name = serializers.CharField(source='host.username', read_only=True)
    
    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'location', 'price_per_night',
            'max_guests', 'bedrooms', 'bathrooms', 'host_name', 'created_at'
        ]


class BookingListSerializer(serializers.ModelSerializer):
    """Simplified serializer for booking list views"""
    listing_title = serializers.CharField(source='listing.title', read_only=True)
    guest_name = serializers.CharField(source='guest.username', read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'listing_title', 'guest_name', 'check_in_date',
            'check_out_date', 'status', 'total_price', 'created_at'
        ]
