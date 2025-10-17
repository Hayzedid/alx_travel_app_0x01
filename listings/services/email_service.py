from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """
    Service class for handling email notifications
    """
    
    @staticmethod
    def send_booking_confirmation_email(booking, payment):
        """
        Send booking confirmation email to customer
        
        Args:
            booking: Booking instance
            payment: Payment instance
        
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            subject = f'Booking Confirmation - {booking.listing.title}'
            
            # Email context
            context = {
                'booking': booking,
                'payment': payment,
                'listing': booking.listing,
                'guest': booking.guest,
                'total_nights': (booking.check_out_date - booking.check_in_date).days,
            }
            
            # Create HTML email content
            html_message = f"""
            <html>
            <body>
                <h2>Booking Confirmation</h2>
                <p>Dear {booking.guest.first_name or booking.guest.username},</p>
                
                <p>Your booking has been confirmed! Here are the details:</p>
                
                <div style="border: 1px solid #ddd; padding: 20px; margin: 20px 0;">
                    <h3>{booking.listing.title}</h3>
                    <p><strong>Location:</strong> {booking.listing.location}</p>
                    <p><strong>Check-in:</strong> {booking.check_in_date}</p>
                    <p><strong>Check-out:</strong> {booking.check_out_date}</p>
                    <p><strong>Guests:</strong> {booking.number_of_guests}</p>
                    <p><strong>Total Amount:</strong> ETB {payment.amount}</p>
                    <p><strong>Payment Reference:</strong> {payment.payment_reference}</p>
                </div>
                
                <p>Thank you for choosing ALX Travel App!</p>
                
                <p>Best regards,<br>ALX Travel Team</p>
            </body>
            </html>
            """
            
            # Plain text version
            plain_message = f"""
            Booking Confirmation
            
            Dear {booking.guest.first_name or booking.guest.username},
            
            Your booking has been confirmed! Here are the details:
            
            Property: {booking.listing.title}
            Location: {booking.listing.location}
            Check-in: {booking.check_in_date}
            Check-out: {booking.check_out_date}
            Guests: {booking.number_of_guests}
            Total Amount: ETB {payment.amount}
            Payment Reference: {payment.payment_reference}
            
            Thank you for choosing ALX Travel App!
            
            Best regards,
            ALX Travel Team
            """
            
            # Send email
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking.guest.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f"Booking confirmation email sent to {booking.guest.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send booking confirmation email: {str(e)}")
            return False
    
    @staticmethod
    def send_payment_failed_email(booking, payment):
        """
        Send payment failed notification email
        
        Args:
            booking: Booking instance
            payment: Payment instance
        
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            subject = f'Payment Failed - {booking.listing.title}'
            
            html_message = f"""
            <html>
            <body>
                <h2>Payment Failed</h2>
                <p>Dear {booking.guest.first_name or booking.guest.username},</p>
                
                <p>Unfortunately, your payment for the following booking could not be processed:</p>
                
                <div style="border: 1px solid #ddd; padding: 20px; margin: 20px 0;">
                    <h3>{booking.listing.title}</h3>
                    <p><strong>Location:</strong> {booking.listing.location}</p>
                    <p><strong>Check-in:</strong> {booking.check_in_date}</p>
                    <p><strong>Check-out:</strong> {booking.check_out_date}</p>
                    <p><strong>Amount:</strong> ETB {payment.amount}</p>
                    <p><strong>Payment Reference:</strong> {payment.payment_reference}</p>
                </div>
                
                <p>Please try again or contact our support team for assistance.</p>
                
                <p>Best regards,<br>ALX Travel Team</p>
            </body>
            </html>
            """
            
            plain_message = f"""
            Payment Failed
            
            Dear {booking.guest.first_name or booking.guest.username},
            
            Unfortunately, your payment for the following booking could not be processed:
            
            Property: {booking.listing.title}
            Location: {booking.listing.location}
            Check-in: {booking.check_in_date}
            Check-out: {booking.check_out_date}
            Amount: ETB {payment.amount}
            Payment Reference: {payment.payment_reference}
            
            Please try again or contact our support team for assistance.
            
            Best regards,
            ALX Travel Team
            """
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking.guest.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f"Payment failed email sent to {booking.guest.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send payment failed email: {str(e)}")
            return False
