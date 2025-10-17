from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Listing, Booking, Review
from .serializers import (
    ListingSerializer, ListingListSerializer,
    BookingSerializer, BookingListSerializer,
    ReviewSerializer
)


class ListingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing travel listings.
    
    Provides CRUD operations for listings with filtering and search capabilities.
    """
    queryset = Listing.objects.filter(is_active=True)
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['location', 'max_guests', 'bedrooms', 'bathrooms', 'host']
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['created_at', 'price_per_night', 'title']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return ListingListSerializer
        return ListingSerializer
    
    def perform_create(self, serializer):
        """Set the host to the current user when creating a listing"""
        serializer.save(host=self.request.user)
    
    @swagger_auto_schema(
        method='get',
        operation_description="Get listings by location",
        manual_parameters=[
            openapi.Parameter(
                'location',
                openapi.IN_QUERY,
                description="Location to filter by",
                type=openapi.TYPE_STRING
            )
        ]
    )
    @action(detail=False, methods=['get'])
    def by_location(self, request):
        """Get listings filtered by location"""
        location = request.query_params.get('location', None)
        if location:
            listings = self.queryset.filter(location__icontains=location)
            serializer = self.get_serializer(listings, many=True)
            return Response(serializer.data)
        return Response({"error": "Location parameter is required"}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        method='get',
        operation_description="Get listings by price range",
        manual_parameters=[
            openapi.Parameter(
                'min_price',
                openapi.IN_QUERY,
                description="Minimum price per night",
                type=openapi.TYPE_NUMBER
            ),
            openapi.Parameter(
                'max_price',
                openapi.IN_QUERY,
                description="Maximum price per night",
                type=openapi.TYPE_NUMBER
            )
        ]
    )
    @action(detail=False, methods=['get'])
    def by_price_range(self, request):
        """Get listings filtered by price range"""
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        
        queryset = self.queryset
        if min_price:
            queryset = queryset.filter(price_per_night__gte=min_price)
        if max_price:
            queryset = queryset.filter(price_per_night__lte=max_price)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        method='get',
        operation_description="Get user's own listings"
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_listings(self, request):
        """Get listings owned by the current user"""
        listings = self.queryset.filter(host=request.user)
        serializer = self.get_serializer(listings, many=True)
        return Response(serializer.data)


class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing bookings.
    
    Provides CRUD operations for bookings with status management.
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'listing', 'guest']
    ordering_fields = ['created_at', 'check_in_date', 'check_out_date']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return BookingListSerializer
        return BookingSerializer
    
    def get_queryset(self):
        """Filter bookings based on user permissions"""
        user = self.request.user
        if user.is_staff:
            return Booking.objects.all()
        # Users can only see their own bookings (as guest or host)
        return Booking.objects.filter(
            Q(guest=user) | Q(listing__host=user)
        )
    
    def perform_create(self, serializer):
        """Set the guest to the current user when creating a booking"""
        serializer.save(guest=self.request.user)
    
    @swagger_auto_schema(
        method='post',
        operation_description="Confirm a booking",
        responses={200: "Booking confirmed successfully"}
    )
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm a booking (only by listing host)"""
        booking = self.get_object()
        
        # Check if user is the host of the listing
        if booking.listing.host != request.user:
            return Response(
                {"error": "Only the listing host can confirm bookings"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if booking.status != 'pending':
            return Response(
                {"error": "Only pending bookings can be confirmed"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'confirmed'
        booking.save()
        
        serializer = self.get_serializer(booking)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        method='post',
        operation_description="Cancel a booking",
        responses={200: "Booking cancelled successfully"}
    )
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a booking (by guest or host)"""
        booking = self.get_object()
        
        # Check if user is the guest or host
        if booking.guest != request.user and booking.listing.host != request.user:
            return Response(
                {"error": "Only the guest or host can cancel bookings"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if booking.status in ['cancelled', 'completed']:
            return Response(
                {"error": f"Cannot cancel a {booking.status} booking"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'cancelled'
        booking.save()
        
        serializer = self.get_serializer(booking)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        method='get',
        operation_description="Get user's bookings as a guest"
    )
    @action(detail=False, methods=['get'])
    def my_bookings(self, request):
        """Get bookings made by the current user"""
        bookings = self.queryset.filter(guest=request.user)
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        method='get',
        operation_description="Get bookings for user's listings"
    )
    @action(detail=False, methods=['get'])
    def host_bookings(self, request):
        """Get bookings for listings owned by the current user"""
        bookings = self.queryset.filter(listing__host=request.user)
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing reviews.
    
    Provides CRUD operations for reviews with validation.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['listing', 'guest', 'rating', 'is_verified']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter reviews based on user permissions"""
        user = self.request.user
        if self.action in ['list', 'retrieve']:
            # Anyone can read reviews
            return Review.objects.all()
        elif user.is_authenticated:
            # Users can only modify their own reviews
            return Review.objects.filter(guest=user)
        return Review.objects.none()
    
    def perform_create(self, serializer):
        """Set the guest to the current user when creating a review"""
        serializer.save(guest=self.request.user)
    
    @swagger_auto_schema(
        method='get',
        operation_description="Get reviews for a specific listing",
        manual_parameters=[
            openapi.Parameter(
                'listing_id',
                openapi.IN_QUERY,
                description="ID of the listing",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ]
    )
    @action(detail=False, methods=['get'])
    def by_listing(self, request):
        """Get reviews for a specific listing"""
        listing_id = request.query_params.get('listing_id')
        if not listing_id:
            return Response(
                {"error": "listing_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reviews = self.queryset.filter(listing_id=listing_id)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        method='get',
        operation_description="Get user's own reviews"
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_reviews(self, request):
        """Get reviews written by the current user"""
        reviews = self.queryset.filter(guest=request.user)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)
