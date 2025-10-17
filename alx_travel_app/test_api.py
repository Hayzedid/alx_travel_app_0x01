#!/usr/bin/env python
"""
API Testing Script for ALX Travel App
This script provides examples of how to test the API endpoints.
"""

import requests
import json
from datetime import date, timedelta


class APITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_listings_endpoint(self):
        """Test the listings endpoint"""
        print("🏠 Testing Listings Endpoint")
        print("-" * 30)
        
        # Test GET /api/listings/
        response = self.session.get(f"{self.base_url}/api/listings/")
        print(f"GET /api/listings/ - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Found {data.get('count', 0)} listings")
        
        # Test listing creation (requires authentication)
        listing_data = {
            "title": "Test API Listing",
            "description": "A test listing created via API",
            "location": "Test City",
            "price_per_night": "150.00",
            "max_guests": 4,
            "bedrooms": 2,
            "bathrooms": 1,
            "amenities": ["wifi", "parking"]
        }
        
        response = self.session.post(
            f"{self.base_url}/api/listings/",
            json=listing_data
        )
        print(f"POST /api/listings/ - Status: {response.status_code}")
        
        if response.status_code == 401:
            print("Authentication required for creating listings")
        
        return response.status_code
    
    def test_bookings_endpoint(self):
        """Test the bookings endpoint"""
        print("\n📅 Testing Bookings Endpoint")
        print("-" * 30)
        
        # Test GET /api/bookings/
        response = self.session.get(f"{self.base_url}/api/bookings/")
        print(f"GET /api/bookings/ - Status: {response.status_code}")
        
        if response.status_code == 401:
            print("Authentication required for accessing bookings")
        
        return response.status_code
    
    def test_reviews_endpoint(self):
        """Test the reviews endpoint"""
        print("\n⭐ Testing Reviews Endpoint")
        print("-" * 30)
        
        # Test GET /api/reviews/
        response = self.session.get(f"{self.base_url}/api/reviews/")
        print(f"GET /api/reviews/ - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Found {data.get('count', 0)} reviews")
        
        return response.status_code
    
    def test_swagger_documentation(self):
        """Test Swagger documentation endpoint"""
        print("\n📚 Testing API Documentation")
        print("-" * 30)
        
        # Test Swagger UI
        response = self.session.get(f"{self.base_url}/swagger/")
        print(f"GET /swagger/ - Status: {response.status_code}")
        
        # Test ReDoc
        response = self.session.get(f"{self.base_url}/redoc/")
        print(f"GET /redoc/ - Status: {response.status_code}")
        
        return response.status_code
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🧪 ALX Travel App API Testing")
        print("=" * 50)
        
        try:
            # Test server connectivity
            response = self.session.get(self.base_url)
            if response.status_code != 200:
                print(f"❌ Server not accessible at {self.base_url}")
                return False
            
            print(f"✅ Server accessible at {self.base_url}")
            
            # Run individual tests
            self.test_listings_endpoint()
            self.test_bookings_endpoint()
            self.test_reviews_endpoint()
            self.test_swagger_documentation()
            
            print("\n🎉 API testing completed!")
            print("\nTo test authenticated endpoints:")
            print("1. Create a superuser: python manage.py createsuperuser")
            print("2. Login via: http://localhost:8000/api-auth/login/")
            print("3. Use the browsable API or Postman with session cookies")
            
            return True
            
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to server at {self.base_url}")
            print("Make sure the Django development server is running:")
            print("python manage.py runserver")
            return False


def main():
    """Main testing function"""
    tester = APITester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
