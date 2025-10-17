#!/usr/bin/env python
"""
Test script for Chapa Payment Integration
Demonstrates the complete payment workflow
"""

import os
import sys
import django
import requests
import json
from decimal import Decimal

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_travel_app.settings')
django.setup()

from django.contrib.auth.models import User
from listings.models import Listing, Booking, Payment
from listings.services.chapa_service import ChapaService

class PaymentIntegrationTester:
    """Test class for payment integration"""
    
    def __init__(self):
        self.base_url = 'http://localhost:8000/api'
        self.token = None
        self.test_user = None
        self.test_listing = None
        self.test_booking = None
    
    def setup_test_data(self):
        """Create test data for payment testing"""
        print("🔧 Setting up test data...")
        
        # Create test user
        self.test_user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        if created:
            self.test_user.set_password('testpass123')
            self.test_user.save()
        
        # Create test host
        test_host, created = User.objects.get_or_create(
            username='testhost',
            defaults={
                'email': 'host@example.com',
                'first_name': 'Test',
                'last_name': 'Host'
            }
        )
        if created:
            test_host.set_password('hostpass123')
            test_host.save()
        
        # Create test listing
        self.test_listing, created = Listing.objects.get_or_create(
            title='Test Hotel Room',
            defaults={
                'description': 'A beautiful test room for payment testing',
                'location': 'Addis Ababa, Ethiopia',
                'price_per_night': Decimal('1000.00'),
                'max_guests': 2,
                'bedrooms': 1,
                'bathrooms': 1,
                'host': test_host,
                'amenities': ['WiFi', 'AC', 'TV']
            }
        )
        
        print(f"✅ Test data created:")
        print(f"   - User: {self.test_user.username}")
        print(f"   - Listing: {self.test_listing.title}")
    
    def authenticate_user(self):
        """Authenticate test user and get token"""
        print("\n🔐 Authenticating user...")
        
        # For this demo, we'll simulate token authentication
        # In real implementation, you'd use your authentication endpoint
        print(f"✅ Authenticated as: {self.test_user.username}")
        self.token = "demo-token"  # Placeholder for actual token
    
    def create_test_booking(self):
        """Create a test booking"""
        print("\n📅 Creating test booking...")
        
        from datetime import date, timedelta
        
        self.test_booking = Booking.objects.create(
            listing=self.test_listing,
            guest=self.test_user,
            check_in_date=date.today() + timedelta(days=7),
            check_out_date=date.today() + timedelta(days=10),
            number_of_guests=2,
            total_price=Decimal('3000.00')  # 3 nights * 1000 ETB
        )
        
        print(f"✅ Booking created:")
        print(f"   - ID: {self.test_booking.id}")
        print(f"   - Total: ETB {self.test_booking.total_price}")
        print(f"   - Dates: {self.test_booking.check_in_date} to {self.test_booking.check_out_date}")
    
    def test_payment_initiation(self):
        """Test payment initiation"""
        print("\n💳 Testing payment initiation...")
        
        try:
            # Initialize Chapa service
            chapa_service = ChapaService()
            
            # Customer data
            customer_data = {
                'first_name': 'Test',
                'last_name': 'Customer',
                'email': 'customer@example.com',
                'phone': '+251911234567'
            }
            
            # Callback and return URLs
            callback_url = 'http://localhost:8000/api/payments/webhook/'
            return_url = 'http://localhost:8000/payment/success'
            
            # Create payment
            result = chapa_service.create_payment_for_booking(
                booking=self.test_booking,
                customer_data=customer_data,
                callback_url=callback_url,
                return_url=return_url
            )
            
            if result['success']:
                print("✅ Payment initiated successfully!")
                print(f"   - Payment Reference: {result['payment'].payment_reference}")
                print(f"   - Checkout URL: {result['checkout_url']}")
                print(f"   - Amount: ETB {result['payment'].amount}")
                
                self.payment = result['payment']
                return True
            else:
                print(f"❌ Payment initiation failed: {result['error']}")
                return False
                
        except Exception as e:
            print(f"❌ Error during payment initiation: {str(e)}")
            return False
    
    def simulate_payment_completion(self):
        """Simulate payment completion via webhook"""
        print("\n🔄 Simulating payment completion...")
        
        if not hasattr(self, 'payment'):
            print("❌ No payment to complete")
            return False
        
        try:
            # Simulate webhook data from Chapa
            webhook_data = {
                'tx_ref': str(self.payment.payment_reference),
                'status': 'success',
                'amount': str(self.payment.amount),
                'currency': 'ETB',
                'created_at': '2025-01-15T10:30:00Z',
                'updated_at': '2025-01-15T10:35:00Z'
            }
            
            # Process webhook
            chapa_service = ChapaService()
            result = chapa_service.handle_webhook(webhook_data)
            
            if result['success']:
                print("✅ Payment completed successfully!")
                
                # Refresh payment from database
                self.payment.refresh_from_db()
                print(f"   - Status: {self.payment.status}")
                print(f"   - Paid at: {self.payment.paid_at}")
                print(f"   - Webhook verified: {self.payment.webhook_verified}")
                
                # Check booking status
                self.test_booking.refresh_from_db()
                print(f"   - Booking status: {self.test_booking.status}")
                
                return True
            else:
                print(f"❌ Payment completion failed: {result['message']}")
                return False
                
        except Exception as e:
            print(f"❌ Error during payment completion: {str(e)}")
            return False
    
    def test_payment_verification(self):
        """Test payment verification"""
        print("\n🔍 Testing payment verification...")
        
        if not hasattr(self, 'payment'):
            print("❌ No payment to verify")
            return False
        
        try:
            chapa_service = ChapaService()
            result = chapa_service.process_payment_verification(self.payment)
            
            print(f"✅ Verification result:")
            print(f"   - Success: {result['success']}")
            print(f"   - Status: {result['status']}")
            print(f"   - Message: {result['message']}")
            
            return result['success']
            
        except Exception as e:
            print(f"❌ Error during payment verification: {str(e)}")
            return False
    
    def test_payment_history(self):
        """Test payment history retrieval"""
        print("\n📊 Testing payment history...")
        
        try:
            payments = Payment.objects.filter(
                booking__guest=self.test_user
            ).select_related('booking', 'booking__listing')
            
            print(f"✅ Found {payments.count()} payment(s):")
            
            for payment in payments:
                print(f"   - Reference: {payment.payment_reference}")
                print(f"   - Amount: ETB {payment.amount}")
                print(f"   - Status: {payment.status}")
                print(f"   - Listing: {payment.booking.listing.title}")
                print(f"   - Created: {payment.created_at}")
                print("   ---")
            
            return True
            
        except Exception as e:
            print(f"❌ Error retrieving payment history: {str(e)}")
            return False
    
    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n🧹 Cleaning up test data...")
        
        try:
            # Delete test payments
            Payment.objects.filter(booking__guest=self.test_user).delete()
            
            # Delete test bookings
            Booking.objects.filter(guest=self.test_user).delete()
            
            # Delete test listings
            Listing.objects.filter(host__username='testhost').delete()
            
            # Delete test users
            User.objects.filter(username__in=['testuser', 'testhost']).delete()
            
            print("✅ Test data cleaned up")
            
        except Exception as e:
            print(f"⚠️  Error during cleanup: {str(e)}")
    
    def run_full_test(self):
        """Run the complete payment integration test"""
        print("🚀 Starting Chapa Payment Integration Test")
        print("=" * 50)
        
        try:
            # Setup
            self.setup_test_data()
            self.authenticate_user()
            self.create_test_booking()
            
            # Test payment workflow
            if self.test_payment_initiation():
                if self.simulate_payment_completion():
                    self.test_payment_verification()
                    self.test_payment_history()
            
            print("\n" + "=" * 50)
            print("✅ Payment integration test completed!")
            
        except Exception as e:
            print(f"\n❌ Test failed with error: {str(e)}")
            
        finally:
            # Cleanup
            cleanup = input("\nClean up test data? (y/n): ")
            if cleanup.lower() == 'y':
                self.cleanup_test_data()

def main():
    """Main function"""
    print("ALX Travel App - Chapa Payment Integration Tester")
    print("=" * 55)
    
    # Check if Chapa API key is configured
    chapa_key = os.getenv('CHAPA_SECRET_KEY')
    if not chapa_key:
        print("⚠️  Warning: CHAPA_SECRET_KEY not configured")
        print("   This test will use mock data for demonstration")
        print("   To test with real Chapa API, set CHAPA_SECRET_KEY environment variable")
    
    print("\nThis script will:")
    print("1. Create test booking data")
    print("2. Initiate a payment with Chapa API")
    print("3. Simulate payment completion")
    print("4. Verify payment status")
    print("5. Display payment history")
    
    proceed = input("\nProceed with test? (y/n): ")
    if proceed.lower() == 'y':
        tester = PaymentIntegrationTester()
        tester.run_full_test()
    else:
        print("Test cancelled.")

if __name__ == "__main__":
    main()
