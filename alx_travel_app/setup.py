#!/usr/bin/env python
"""
Setup script for ALX Travel App API
This script helps initialize the project for development.
"""

import os
import sys
import subprocess


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False


def main():
    """Main setup function"""
    print("🚀 Setting up ALX Travel App API")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Setup steps
    steps = [
        ("python manage.py makemigrations", "Creating database migrations"),
        ("python manage.py migrate", "Applying database migrations"),
        ("python manage.py collectstatic --noinput", "Collecting static files"),
    ]
    
    success_count = 0
    for command, description in steps:
        if run_command(command, description):
            success_count += 1
    
    print(f"\n📊 Setup Results: {success_count}/{len(steps)} steps completed successfully")
    
    if success_count == len(steps):
        print("\n🎉 Project setup completed successfully!")
        print("\nNext steps:")
        print("1. Create a superuser: python manage.py createsuperuser")
        print("2. Run the development server: python manage.py runserver")
        print("3. Visit the API documentation: http://localhost:8000/swagger/")
        print("4. Test the API endpoints using Postman or the browsable API")
    else:
        print("\n⚠️  Some setup steps failed. Please check the errors above.")


if __name__ == "__main__":
    main()
