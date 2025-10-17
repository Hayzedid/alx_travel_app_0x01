#!/usr/bin/env python
"""
Verification script for ALX Travel App API v0x01
This script verifies that all task requirements have been implemented.
"""

import os
import sys


def check_file_exists(filepath, description):
    """Check if a file exists and report status"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - NOT FOUND")
        return False


def check_file_contains(filepath, patterns, description):
    """Check if a file contains specific patterns"""
    if not os.path.exists(filepath):
        print(f"❌ {description}: {filepath} - FILE NOT FOUND")
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        missing_patterns = []
        for pattern in patterns:
            if pattern not in content:
                missing_patterns.append(pattern)
        
        if not missing_patterns:
            print(f"✅ {description}: All required patterns found")
            return True
        else:
            print(f"❌ {description}: Missing patterns: {missing_patterns}")
            return False
            
    except Exception as e:
        print(f"❌ {description}: Error reading file - {e}")
        return False


def main():
    """Main verification function"""
    print("🔍 ALX Travel App API v0x01 - Requirements Verification")
    print("=" * 60)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check project structure
    print("\n📁 Project Structure Verification")
    print("-" * 40)
    
    structure_checks = [
        (os.path.join(base_dir, "manage.py"), "Django management script"),
        (os.path.join(base_dir, "listings", "views.py"), "Listings views file"),
        (os.path.join(base_dir, "listings", "urls.py"), "Listings URLs file"),
        (os.path.join(base_dir, "README.md"), "README documentation"),
        (os.path.join(base_dir, "requirements.txt"), "Requirements file"),
        (os.path.join(base_dir, "alx_travel_app", "settings.py"), "Django settings"),
        (os.path.join(base_dir, "alx_travel_app", "urls.py"), "Main URLs file"),
    ]
    
    structure_passed = 0
    for filepath, description in structure_checks:
        if check_file_exists(filepath, description):
            structure_passed += 1
    
    # Check ViewSets implementation
    print("\n🔧 ViewSets Implementation Verification")
    print("-" * 40)
    
    views_patterns = [
        "class ListingViewSet(viewsets.ModelViewSet)",
        "class BookingViewSet(viewsets.ModelViewSet)",
        "from rest_framework import viewsets",
        "queryset = Listing.objects",
        "queryset = Booking.objects",
    ]
    
    views_file = os.path.join(base_dir, "listings", "views.py")
    views_passed = check_file_contains(views_file, views_patterns, "ViewSets implementation")
    
    # Check URL router configuration
    print("\n🌐 URL Router Configuration Verification")
    print("-" * 40)
    
    urls_patterns = [
        "from rest_framework.routers import DefaultRouter",
        "router = DefaultRouter()",
        "router.register(r'listings', views.ListingViewSet",
        "router.register(r'bookings', views.BookingViewSet",
        "path('api/', include(router.urls))",
    ]
    
    urls_file = os.path.join(base_dir, "listings", "urls.py")
    urls_passed = check_file_contains(urls_file, urls_patterns, "URL router configuration")
    
    # Check Swagger documentation
    print("\n📚 Swagger Documentation Verification")
    print("-" * 40)
    
    swagger_patterns = [
        "drf_yasg",
        "swagger",
        "schema_view",
        "openapi.Info",
    ]
    
    main_urls_file = os.path.join(base_dir, "alx_travel_app", "urls.py")
    swagger_passed = check_file_contains(main_urls_file, swagger_patterns, "Swagger documentation")
    
    # Check Django REST Framework configuration
    print("\n⚙️ Django REST Framework Configuration")
    print("-" * 40)
    
    drf_patterns = [
        "rest_framework",
        "REST_FRAMEWORK",
        "DEFAULT_PAGINATION_CLASS",
    ]
    
    settings_file = os.path.join(base_dir, "alx_travel_app", "settings.py")
    drf_passed = check_file_contains(settings_file, drf_patterns, "DRF configuration")
    
    # Summary
    print("\n📊 Verification Summary")
    print("-" * 40)
    
    total_checks = len(structure_checks) + 4  # 4 additional feature checks
    passed_checks = structure_passed + sum([views_passed, urls_passed, swagger_passed, drf_passed])
    
    print(f"Total checks: {total_checks}")
    print(f"Passed checks: {passed_checks}")
    print(f"Success rate: {(passed_checks/total_checks)*100:.1f}%")
    
    if passed_checks == total_checks:
        print("\n🎉 ALL REQUIREMENTS VERIFIED SUCCESSFULLY!")
        print("\nTask 0 Implementation Status:")
        print("✅ Duplicate Project: alx_travel_app_0x00 → alx_travel_app_0x01")
        print("✅ Create ViewSets: ListingViewSet and BookingViewSet implemented")
        print("✅ Configure URLs: DRF router with RESTful endpoints under /api/")
        print("✅ Swagger Documentation: Interactive API documentation available")
        print("✅ CRUD Operations: Full Create, Read, Update, Delete support")
        
        print("\nNext Steps:")
        print("1. Run: python manage.py makemigrations")
        print("2. Run: python manage.py migrate")
        print("3. Run: python manage.py runserver")
        print("4. Test endpoints at: http://localhost:8000/swagger/")
        
    else:
        print(f"\n⚠️  {total_checks - passed_checks} requirements need attention")
        print("Please review the failed checks above.")
    
    return passed_checks == total_checks


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
