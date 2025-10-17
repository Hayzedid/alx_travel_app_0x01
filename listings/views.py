from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Listing, Booking, Review, Payment
from .serializers import (
    ListingSerializer, ListingListSerializer,
    BookingSerializer, BookingListSerializer,
    ReviewSerializer
)
from .services.chapa_service import ChapaService
from .services.email_service import EmailService


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


class PaymentViewSet(viewsets.ViewSet):
    """
    ViewSet for handling payment operations with Chapa API
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        method='post',
        operation_description="Initiate payment for a booking",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['booking_id', 'customer_data'],
            properties={
                'booking_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Booking ID'),
                'customer_data': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'email': openapi.Schema(type=openapi.TYPE_STRING),
                        'phone': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                ),
                'return_url': openapi.Schema(type=openapi.TYPE_STRING, description='Return URL after payment'),
            }
        ),
        responses={
            200: openapi.Response(
                description="Payment initiated successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'checkout_url': openapi.Schema(type=openapi.TYPE_STRING),
                        'payment_reference': openapi.Schema(type=openapi.TYPE_STRING),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: openapi.Response(description="Bad request"),
            404: openapi.Response(description="Booking not found"),
        }
    )
    @action(detail=False, methods=['post'])
    def initiate(self, request):
        """Initiate payment for a booking"""
        try:
            booking_id = request.data.get('booking_id')
            customer_data = request.data.get('customer_data', {})
            return_url = request.data.get('return_url', 'https://alx-travel-app.com/payment/success')
            
            if not booking_id:
                return Response(
                    {'error': 'booking_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get booking
            try:
                booking = Booking.objects.get(id=booking_id, guest=request.user)
            except Booking.DoesNotExist:
                return Response(
                    {'error': 'Booking not found or not owned by user'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check if booking already has a successful payment
            if hasattr(booking, 'payment') and booking.payment.is_successful:
                return Response(
                    {'error': 'Booking already paid'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate customer data
            required_fields = ['first_name', 'last_name', 'email']
            for field in required_fields:
                if not customer_data.get(field):
                    return Response(
                        {'error': f'{field} is required in customer_data'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Create callback URL
            callback_url = request.build_absolute_uri('/api/payments/webhook/')
            
            # Initialize Chapa service and create payment
            chapa_service = ChapaService()
            result = chapa_service.create_payment_for_booking(
                booking=booking,
                customer_data=customer_data,
                callback_url=callback_url,
                return_url=return_url
            )
            
            if result['success']:
                return Response({
                    'success': True,
                    'checkout_url': result['checkout_url'],
                    'payment_reference': str(result['payment'].payment_reference),
                    'message': 'Payment initiated successfully'
                })
            else:
                return Response(
                    {'error': result['error']},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {'error': f'Payment initiation failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        method='get',
        operation_description="Verify payment status",
        manual_parameters=[
            openapi.Parameter(
                'payment_reference',
                openapi.IN_QUERY,
                description="Payment reference to verify",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Payment verification result",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'payment_data': openapi.Schema(type=openapi.TYPE_OBJECT),
                    }
                )
            ),
            400: openapi.Response(description="Bad request"),
            404: openapi.Response(description="Payment not found"),
        }
    )
    @action(detail=False, methods=['get'])
    def verify(self, request):
        """Verify payment status"""
        try:
            payment_reference = request.query_params.get('payment_reference')
            
            if not payment_reference:
                return Response(
                    {'error': 'payment_reference is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get payment
            try:
                payment = Payment.objects.get(
                    payment_reference=payment_reference,
                    booking__guest=request.user
                )
            except Payment.DoesNotExist:
                return Response(
                    {'error': 'Payment not found or not owned by user'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verify payment with Chapa
            chapa_service = ChapaService()
            result = chapa_service.process_payment_verification(payment)
            
            # Send confirmation email if payment completed
            if result['success'] and result['status'] == 'completed':
                EmailService.send_booking_confirmation_email(payment.booking, payment)
            
            return Response({
                'success': result['success'],
                'status': result['status'],
                'message': result['message'],
                'payment_data': {
                    'payment_reference': str(payment.payment_reference),
                    'amount': str(payment.amount),
                    'currency': payment.currency,
                    'status': payment.status,
                    'created_at': payment.created_at,
                    'paid_at': payment.paid_at,
                }
            })
            
        except Exception as e:
            return Response(
                {'error': f'Payment verification failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        method='post',
        operation_description="Chapa webhook endpoint for payment notifications",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description="Webhook payload from Chapa"
        ),
        responses={
            200: openapi.Response(description="Webhook processed successfully"),
            400: openapi.Response(description="Bad request"),
        }
    )
    @action(detail=False, methods=['post'], permission_classes=[])
    def webhook(self, request):
        """Handle Chapa webhook notifications"""
        try:
            webhook_data = request.data
            
            # Initialize Chapa service and process webhook
            chapa_service = ChapaService()
            result = chapa_service.handle_webhook(webhook_data)
            
            if result['success']:
                # If payment completed, send confirmation email
                tx_ref = webhook_data.get('tx_ref')
                if tx_ref and webhook_data.get('status') == 'success':
                    try:
                        payment = Payment.objects.get(payment_reference=tx_ref)
                        EmailService.send_booking_confirmation_email(payment.booking, payment)
                    except Payment.DoesNotExist:
                        pass
                
                return Response({'message': result['message']})
            else:
                return Response(
                    {'error': result['message']},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {'error': f'Webhook processing failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        method='get',
        operation_description="Get user's payment history",
        responses={
            200: openapi.Response(
                description="Payment history",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'payment_reference': openapi.Schema(type=openapi.TYPE_STRING),
                            'amount': openapi.Schema(type=openapi.TYPE_STRING),
                            'currency': openapi.Schema(type=openapi.TYPE_STRING),
                            'status': openapi.Schema(type=openapi.TYPE_STRING),
                            'booking_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'listing_title': openapi.Schema(type=openapi.TYPE_STRING),
                            'created_at': openapi.Schema(type=openapi.TYPE_STRING),
                            'paid_at': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    )
                )
            )
        }
    )
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get user's payment history"""
        try:
            payments = Payment.objects.filter(
                booking__guest=request.user
            ).select_related('booking', 'booking__listing').order_by('-created_at')
            
            payment_data = []
            for payment in payments:
                payment_data.append({
                    'payment_reference': str(payment.payment_reference),
                    'amount': str(payment.amount),
                    'currency': payment.currency,
                    'status': payment.status,
                    'booking_id': payment.booking.id,
                    'listing_title': payment.booking.listing.title,
                    'listing_location': payment.booking.listing.location,
                    'check_in_date': payment.booking.check_in_date,
                    'check_out_date': payment.booking.check_out_date,
                    'created_at': payment.created_at,
                    'paid_at': payment.paid_at,
                })
            
            return Response(payment_data)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to retrieve payment history: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
