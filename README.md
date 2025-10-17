# ALX Travel App v0x02 - Chapa Payment Integration

A comprehensive travel booking application with integrated Chapa payment processing, built with Django REST Framework.

## 🚀 Features

### Core Features
- **Travel Listings Management**: Create, view, update, and delete travel listings
- **Booking System**: Complete booking workflow with date validation
- **Review System**: Guest reviews and ratings for completed stays
- **User Authentication**: Secure user registration and authentication

### 🆕 Payment Integration (v0x02)
- **Chapa API Integration**: Secure payment processing with Ethiopian payment gateway
- **Payment Workflow**: Complete payment lifecycle from initiation to verification
- **Webhook Support**: Real-time payment status updates via Chapa webhooks
- **Email Notifications**: Automated confirmation emails for successful payments
- **Payment History**: Complete payment tracking and history for users
- **Error Handling**: Comprehensive error handling and retry mechanisms

## 📋 Prerequisites

- Python 3.8+
- Django 4.2+
- Chapa API Account (https://developer.chapa.co/)
- Redis (for background tasks)

## 🛠️ Installation & Setup

### 1. Clone and Setup Project
```bash
cd alx_travel_app_0x02
pip install -r requirements.txt
```

### 2. Environment Configuration
Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Update the following in your `.env` file:
```env
# Chapa API Configuration
CHAPA_SECRET_KEY=your-chapa-secret-key-here
CHAPA_PUBLIC_KEY=your-chapa-public-key-here

# Email Configuration (for notifications)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
```

### 3. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 4. Start Development Server
```bash
python manage.py runserver
```

### 5. Start Background Tasks (Optional)
For email notifications:
```bash
# Start Redis server
redis-server

# Start Celery worker
celery -A alx_travel_app worker --loglevel=info
```

## 🔧 Chapa API Setup

### 1. Create Chapa Account
1. Visit [Chapa Developer Portal](https://developer.chapa.co/)
2. Create an account and verify your email
3. Navigate to API Keys section
4. Copy your Secret Key and Public Key

### 2. Configure Webhook (Optional)
For real-time payment updates:
1. In Chapa dashboard, go to Webhooks
2. Add webhook URL: `https://yourdomain.com/api/payments/webhook/`
3. Select payment events to receive

## 🌐 API Endpoints

### Payment Endpoints

#### Initiate Payment
```http
POST /api/payments/initiate/
Authorization: Bearer <token>
Content-Type: application/json

{
    "booking_id": 1,
    "customer_data": {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone": "+251911234567"
    },
    "return_url": "https://yourapp.com/payment/success"
}
```

#### Verify Payment
```http
GET /api/payments/verify/?payment_reference=<reference>
Authorization: Bearer <token>
```

#### Payment History
```http
GET /api/payments/history/
Authorization: Bearer <token>
```

#### Webhook Endpoint (Chapa)
```http
POST /api/payments/webhook/
Content-Type: application/json

{
    "tx_ref": "payment-reference",
    "status": "success",
    "amount": "1000.00",
    "currency": "ETB"
}
```

## 💳 Payment Workflow

### 1. Create Booking
```python
# User creates a booking through the booking API
POST /api/bookings/
{
    "listing": 1,
    "check_in_date": "2025-01-15",
    "check_out_date": "2025-01-20",
    "number_of_guests": 2
}
```

### 2. Initiate Payment
```python
# Initiate payment for the booking
POST /api/payments/initiate/
{
    "booking_id": 1,
    "customer_data": {...}
}

# Response includes checkout URL
{
    "success": true,
    "checkout_url": "https://checkout.chapa.co/...",
    "payment_reference": "uuid-reference"
}
```

### 3. Customer Payment
- User is redirected to Chapa checkout page
- Customer completes payment using various methods:
  - Mobile Money (Telebirr, M-Birr)
  - Bank Transfer
  - Credit/Debit Cards

### 4. Payment Verification
```python
# Verify payment status
GET /api/payments/verify/?payment_reference=<reference>

# Automatic verification via webhook
POST /api/payments/webhook/ (called by Chapa)
```

### 5. Confirmation
- Payment status updated in database
- Booking status changed to 'confirmed'
- Confirmation email sent to customer

## 🧪 Testing Payment Integration

### Sandbox Testing
Chapa provides a sandbox environment for testing:

1. Use sandbox API keys in development
2. Test with sandbox payment methods
3. Verify webhook functionality

### Test Payment Flow
```python
# Example test payment data
{
    "booking_id": 1,
    "customer_data": {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "phone": "+251911111111"
    }
}
```

## 📊 Payment Model Structure

```python
class Payment(models.Model):
    booking = models.OneToOneField(Booking)
    payment_reference = models.CharField(unique=True)
    transaction_id = models.CharField()
    amount = models.DecimalField()
    currency = models.CharField(default='ETB')
    status = models.CharField(choices=PAYMENT_STATUS_CHOICES)
    chapa_checkout_url = models.URLField()
    chapa_response = models.JSONField()
    customer_email = models.EmailField()
    customer_phone = models.CharField()
    customer_name = models.CharField()
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True)
    webhook_verified = models.BooleanField(default=False)
```

## 🔒 Security Features

- **API Key Security**: Environment variable storage
- **User Authentication**: JWT token-based authentication
- **Payment Validation**: Comprehensive input validation
- **Webhook Verification**: Secure webhook processing
- **Error Handling**: Graceful error handling and logging

## 📧 Email Notifications

Automated emails are sent for:
- **Payment Confirmation**: Successful payment completion
- **Payment Failure**: Failed payment attempts
- **Booking Updates**: Status changes and confirmations

## 🚨 Error Handling

The system handles various error scenarios:
- **Network Errors**: Retry mechanisms for API calls
- **Invalid Payments**: Validation and error messages
- **Webhook Failures**: Logging and manual verification options
- **Email Failures**: Fallback notification methods

## 📈 Monitoring & Logging

- **Payment Tracking**: Complete audit trail for all payments
- **Error Logging**: Comprehensive error logging and monitoring
- **Webhook Logs**: All webhook events are logged
- **Performance Monitoring**: API response time tracking

## 🔧 Configuration Options

### Payment Settings
```python
# settings.py
CHAPA_SECRET_KEY = os.getenv('CHAPA_SECRET_KEY')
CHAPA_BASE_URL = 'https://api.chapa.co/v1'
PAYMENT_TIMEOUT = 30  # seconds
MAX_VERIFICATION_ATTEMPTS = 3
```

### Email Settings
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@alx-travel-app.com'
```

## 🚀 Deployment

### Production Checklist
- [ ] Set `DEBUG=False`
- [ ] Configure production database
- [ ] Set up Redis for Celery
- [ ] Configure email backend
- [ ] Set up Chapa webhook URL
- [ ] Configure logging
- [ ] Set up monitoring

### Environment Variables
```env
DEBUG=False
SECRET_KEY=production-secret-key
DATABASE_URL=postgresql://...
CHAPA_SECRET_KEY=live-chapa-secret-key
EMAIL_HOST_USER=production-email
REDIS_URL=redis://production-redis
```

## 📚 API Documentation

Interactive API documentation is available at:
- **Swagger UI**: `http://localhost:8000/swagger/`
- **ReDoc**: `http://localhost:8000/redoc/`

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
pytest
```

## 📞 Support

For Chapa API support:
- **Documentation**: https://developer.chapa.co/docs
- **Support**: support@chapa.co

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

**Status**: ✅ Complete Chapa Payment Integration Ready for Production