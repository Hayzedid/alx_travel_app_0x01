# ALX Travel App API - Version 0x01

A comprehensive Django REST API for managing travel listings, bookings, and reviews. This project implements full CRUD operations with proper authentication, filtering, and Swagger documentation.

## 🚀 Features

### API Endpoints

#### Listings Management
- **GET /api/listings/** - List all active listings with pagination
- **POST /api/listings/** - Create a new listing (authenticated users)
- **GET /api/listings/{id}/** - Retrieve a specific listing
- **PUT /api/listings/{id}/** - Update a listing (owner only)
- **PATCH /api/listings/{id}/** - Partially update a listing (owner only)
- **DELETE /api/listings/{id}/** - Delete a listing (owner only)

#### Custom Listing Endpoints
- **GET /api/listings/by_location/?location={location}** - Filter listings by location
- **GET /api/listings/by_price_range/?min_price={min}&max_price={max}** - Filter by price range
- **GET /api/listings/my_listings/** - Get current user's listings

#### Bookings Management
- **GET /api/bookings/** - List user's bookings (filtered by permissions)
- **POST /api/bookings/** - Create a new booking (authenticated users)
- **GET /api/bookings/{id}/** - Retrieve a specific booking
- **PUT /api/bookings/{id}/** - Update a booking
- **PATCH /api/bookings/{id}/** - Partially update a booking
- **DELETE /api/bookings/{id}/** - Cancel a booking

#### Custom Booking Endpoints
- **POST /api/bookings/{id}/confirm/** - Confirm a booking (host only)
- **POST /api/bookings/{id}/cancel/** - Cancel a booking (guest or host)
- **GET /api/bookings/my_bookings/** - Get user's bookings as guest
- **GET /api/bookings/host_bookings/** - Get bookings for user's listings

#### Reviews Management
- **GET /api/reviews/** - List all reviews
- **POST /api/reviews/** - Create a new review (authenticated users)
- **GET /api/reviews/{id}/** - Retrieve a specific review
- **PUT /api/reviews/{id}/** - Update a review (author only)
- **PATCH /api/reviews/{id}/** - Partially update a review (author only)
- **DELETE /api/reviews/{id}/** - Delete a review (author only)

#### Custom Review Endpoints
- **GET /api/reviews/by_listing/?listing_id={id}** - Get reviews for a specific listing
- **GET /api/reviews/my_reviews/** - Get current user's reviews

## 🛠 Installation & Setup

### Prerequisites
- Python 3.8+
- pip
- virtualenv (recommended)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd alx_travel_app_0x01
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

5. **Database setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/`

## 📚 API Documentation

### Swagger UI
Access interactive API documentation at:
- **Swagger UI**: `http://localhost:8000/swagger/`
- **ReDoc**: `http://localhost:8000/redoc/`

### Authentication
The API supports session-based authentication. For API testing:
- Use the browsable API at `http://localhost:8000/api-auth/login/`
- Or authenticate via session cookies

## 🧪 Testing

### Run Tests
```bash
python manage.py test
```

### API Testing with Postman

#### 1. Create a Listing
```http
POST /api/listings/
Content-Type: application/json

{
    "title": "Beautiful Beach House",
    "description": "A stunning beachfront property with ocean views",
    "location": "Miami Beach",
    "price_per_night": "250.00",
    "max_guests": 6,
    "bedrooms": 3,
    "bathrooms": 2,
    "amenities": ["wifi", "pool", "beach_access", "parking"]
}
```

#### 2. Create a Booking
```http
POST /api/bookings/
Content-Type: application/json

{
    "listing_id": 1,
    "check_in_date": "2024-12-01",
    "check_out_date": "2024-12-05",
    "number_of_guests": 4,
    "total_price": "1000.00",
    "special_requests": "Late check-in requested"
}
```

#### 3. Create a Review
```http
POST /api/reviews/
Content-Type: application/json

{
    "listing_id": 1,
    "booking_id": 1,
    "rating": 5,
    "title": "Amazing stay!",
    "comment": "The property exceeded our expectations. Great location and amenities."
}
```

## 🏗 Project Structure

```
alx_travel_app_0x01/
├── alx_travel_app/
│   ├── __init__.py
│   ├── settings.py          # Django settings with DRF and Swagger config
│   ├── urls.py              # Main URL configuration
│   ├── wsgi.py              # WSGI configuration
│   └── asgi.py              # ASGI configuration
├── listings/
│   ├── __init__.py
│   ├── models.py            # Listing, Booking, Review models
│   ├── serializers.py       # DRF serializers for API
│   ├── views.py             # ViewSets with CRUD operations
│   ├── urls.py              # API URL routing with DRF router
│   ├── admin.py             # Django admin configuration
│   ├── apps.py              # App configuration
│   └── tests.py             # Unit and API tests
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## 🔧 Models

### Listing Model
- **Fields**: title, description, location, price_per_night, max_guests, bedrooms, bathrooms, amenities, host, created_at, updated_at, is_active
- **Relationships**: ForeignKey to User (host)

### Booking Model
- **Fields**: listing, guest, check_in_date, check_out_date, number_of_guests, total_price, status, special_requests, created_at, updated_at
- **Status Choices**: pending, confirmed, cancelled, completed
- **Relationships**: ForeignKey to Listing and User (guest)

### Review Model
- **Fields**: listing, guest, booking, rating, title, comment, created_at, updated_at, is_verified
- **Relationships**: ForeignKey to Listing, User (guest), and OneToOne to Booking

## 🔒 Permissions & Security

- **Listings**: Read access for all, write access for authenticated users (owners only for updates/deletes)
- **Bookings**: Full access for authenticated users (filtered by user permissions)
- **Reviews**: Read access for all, write access for authenticated users (authors only for updates/deletes)

## 🎯 Key Features

### Filtering & Search
- **Listings**: Filter by location, guests, bedrooms, bathrooms, host
- **Bookings**: Filter by status, listing, guest
- **Reviews**: Filter by listing, guest, rating, verification status
- **Search**: Full-text search on listing titles, descriptions, and locations

### Pagination
- Default page size: 10 items
- Configurable via `PAGE_SIZE` setting

### Validation
- Custom validation for booking dates, guest capacity, and review ratings
- Model-level validation with clean methods
- Serializer-level validation for API inputs

### Custom Actions
- Listing filtering by location and price range
- Booking confirmation and cancellation workflows
- User-specific listing and booking queries

## 🚀 Deployment Considerations

### Environment Variables
Configure the following in production:
- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to False
- `ALLOWED_HOSTS`: Your domain names
- `DATABASE_URL`: Production database connection

### Database
- Development: SQLite (default)
- Production: PostgreSQL recommended

### Static Files
Configure static file serving for production deployment.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run tests to ensure everything works
6. Submit a pull request

## 📝 License

This project is part of the ALX Software Engineering program.

## 📞 Support

For questions or issues, please contact the development team or create an issue in the repository.

---

**ALX Travel App API v0x01** - Built with Django REST Framework
