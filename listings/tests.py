from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from datetime import date, timedelta

from .models import Listing, Booking, Review


class ListingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testhost',
            email='host@test.com',
            password='testpass123'
        )
        
    def test_listing_creation(self):
        listing = Listing.objects.create(
            title='Test Listing',
            description='A test listing',
            location='Test City',
            price_per_night=Decimal('100.00'),
            max_guests=4,
            bedrooms=2,
            bathrooms=1,
            host=self.user
        )
        self.assertEqual(str(listing), 'Test Listing - Test City')
        self.assertTrue(listing.is_active)


class BookingModelTest(TestCase):
    def setUp(self):
        self.host = User.objects.create_user(
            username='testhost',
            email='host@test.com',
            password='testpass123'
        )
        self.guest = User.objects.create_user(
            username='testguest',
            email='guest@test.com',
            password='testpass123'
        )
        self.listing = Listing.objects.create(
            title='Test Listing',
            description='A test listing',
            location='Test City',
            price_per_night=Decimal('100.00'),
            max_guests=4,
            bedrooms=2,
            bathrooms=1,
            host=self.host
        )
        
    def test_booking_creation(self):
        booking = Booking.objects.create(
            listing=self.listing,
            guest=self.guest,
            check_in_date=date.today() + timedelta(days=1),
            check_out_date=date.today() + timedelta(days=3),
            number_of_guests=2,
            total_price=Decimal('200.00')
        )
        self.assertEqual(booking.status, 'pending')
        self.assertEqual(booking.number_of_guests, 2)


class ListingAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.listing = Listing.objects.create(
            title='API Test Listing',
            description='A test listing for API',
            location='API City',
            price_per_night=Decimal('150.00'),
            max_guests=6,
            bedrooms=3,
            bathrooms=2,
            host=self.user
        )
        
    def test_get_listings(self):
        url = reverse('listing-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
    def test_create_listing_authenticated(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('listing-list')
        data = {
            'title': 'New Listing',
            'description': 'A new test listing',
            'location': 'New City',
            'price_per_night': '200.00',
            'max_guests': 4,
            'bedrooms': 2,
            'bathrooms': 1,
            'amenities': ['wifi', 'parking']
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_create_listing_unauthenticated(self):
        url = reverse('listing-list')
        data = {
            'title': 'New Listing',
            'description': 'A new test listing',
            'location': 'New City',
            'price_per_night': '200.00',
            'max_guests': 4,
            'bedrooms': 2,
            'bathrooms': 1
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BookingAPITest(APITestCase):
    def setUp(self):
        self.host = User.objects.create_user(
            username='testhost',
            email='host@test.com',
            password='testpass123'
        )
        self.guest = User.objects.create_user(
            username='testguest',
            email='guest@test.com',
            password='testpass123'
        )
        self.listing = Listing.objects.create(
            title='Booking Test Listing',
            description='A test listing for booking',
            location='Booking City',
            price_per_night=Decimal('100.00'),
            max_guests=4,
            bedrooms=2,
            bathrooms=1,
            host=self.host
        )
        
    def test_create_booking(self):
        self.client.force_authenticate(user=self.guest)
        url = reverse('booking-list')
        data = {
            'listing_id': self.listing.id,
            'check_in_date': str(date.today() + timedelta(days=1)),
            'check_out_date': str(date.today() + timedelta(days=3)),
            'number_of_guests': 2,
            'total_price': '200.00'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_booking_requires_authentication(self):
        url = reverse('booking-list')
        data = {
            'listing_id': self.listing.id,
            'check_in_date': str(date.today() + timedelta(days=1)),
            'check_out_date': str(date.today() + timedelta(days=3)),
            'number_of_guests': 2,
            'total_price': '200.00'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
