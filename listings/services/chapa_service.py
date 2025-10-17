import requests
import os
import logging
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from ..models import Payment

logger = logging.getLogger(__name__)

class ChapaService:
    """
    Service class for handling Chapa API interactions
    """
    
    def __init__(self):
        self.secret_key = os.getenv('CHAPA_SECRET_KEY')
        self.base_url = 'https://api.chapa.co/v1'
        self.sandbox_url = 'https://api.chapa.co/v1'  # Chapa uses same URL for sandbox
        
        if not self.secret_key:
            raise ValueError("CHAPA_SECRET_KEY environment variable is required")
    
    def get_headers(self):
        """Get headers for Chapa API requests"""
        return {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json',
        }
    
    def initiate_payment(self, payment_data):
        """
        Initiate payment with Chapa API
        
        Args:
            payment_data (dict): Payment information
                - amount: Payment amount
                - currency: Currency (ETB)
                - email: Customer email
                - first_name: Customer first name
                - last_name: Customer last name
                - phone_number: Customer phone (optional)
                - tx_ref: Transaction reference
                - callback_url: Callback URL for payment completion
                - return_url: Return URL after payment
                - description: Payment description
        
        Returns:
            dict: Chapa API response
        """
        url = f"{self.base_url}/transaction/initialize"
        
        try:
            response = requests.post(
                url,
                json=payment_data,
                headers=self.get_headers(),
                timeout=30
            )
            
            response_data = response.json()
            
            if response.status_code == 200 and response_data.get('status') == 'success':
                logger.info(f"Payment initiated successfully: {payment_data['tx_ref']}")
                return {
                    'success': True,
                    'data': response_data['data'],
                    'checkout_url': response_data['data']['checkout_url']
                }
            else:
                logger.error(f"Payment initiation failed: {response_data}")
                return {
                    'success': False,
                    'error': response_data.get('message', 'Payment initiation failed'),
                    'data': response_data
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during payment initiation: {str(e)}")
            return {
                'success': False,
                'error': f'Network error: {str(e)}',
                'data': {}
            }
        except Exception as e:
            logger.error(f"Unexpected error during payment initiation: {str(e)}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'data': {}
            }
    
    def verify_payment(self, tx_ref):
        """
        Verify payment status with Chapa API
        
        Args:
            tx_ref (str): Transaction reference
        
        Returns:
            dict: Verification response
        """
        url = f"{self.base_url}/transaction/verify/{tx_ref}"
        
        try:
            response = requests.get(
                url,
                headers=self.get_headers(),
                timeout=30
            )
            
            response_data = response.json()
            
            if response.status_code == 200 and response_data.get('status') == 'success':
                transaction_data = response_data['data']
                logger.info(f"Payment verification successful: {tx_ref}")
                
                return {
                    'success': True,
                    'status': transaction_data.get('status'),
                    'data': transaction_data
                }
            else:
                logger.error(f"Payment verification failed: {response_data}")
                return {
                    'success': False,
                    'error': response_data.get('message', 'Payment verification failed'),
                    'data': response_data
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during payment verification: {str(e)}")
            return {
                'success': False,
                'error': f'Network error: {str(e)}',
                'data': {}
            }
        except Exception as e:
            logger.error(f"Unexpected error during payment verification: {str(e)}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'data': {}
            }
    
    def create_payment_for_booking(self, booking, customer_data, callback_url, return_url):
        """
        Create a payment record and initiate payment with Chapa
        
        Args:
            booking: Booking instance
            customer_data (dict): Customer information
            callback_url (str): Webhook callback URL
            return_url (str): Return URL after payment
        
        Returns:
            dict: Payment creation result
        """
        try:
            # Create payment record
            payment = Payment.objects.create(
                booking=booking,
                amount=booking.total_price,
                customer_email=customer_data['email'],
                customer_phone=customer_data.get('phone', ''),
                customer_name=f"{customer_data['first_name']} {customer_data['last_name']}"
            )
            
            # Prepare payment data for Chapa
            payment_data = {
                'amount': str(booking.total_price),
                'currency': 'ETB',
                'email': customer_data['email'],
                'first_name': customer_data['first_name'],
                'last_name': customer_data['last_name'],
                'phone_number': customer_data.get('phone', ''),
                'tx_ref': str(payment.payment_reference),
                'callback_url': callback_url,
                'return_url': return_url,
                'description': f'Payment for booking {booking.id} - {booking.listing.title}',
                'customization': {
                    'title': 'ALX Travel App',
                    'description': f'Booking payment for {booking.listing.title}'
                }
            }
            
            # Initiate payment with Chapa
            chapa_response = self.initiate_payment(payment_data)
            
            if chapa_response['success']:
                # Update payment record with Chapa response
                payment.chapa_checkout_url = chapa_response['checkout_url']
                payment.chapa_response = chapa_response['data']
                payment.status = 'processing'
                payment.save()
                
                return {
                    'success': True,
                    'payment': payment,
                    'checkout_url': chapa_response['checkout_url']
                }
            else:
                # Mark payment as failed
                payment.mark_as_failed(chapa_response['error'])
                
                return {
                    'success': False,
                    'error': chapa_response['error'],
                    'payment': payment
                }
                
        except Exception as e:
            logger.error(f"Error creating payment for booking {booking.id}: {str(e)}")
            return {
                'success': False,
                'error': f'Payment creation failed: {str(e)}',
                'payment': None
            }
    
    def process_payment_verification(self, payment):
        """
        Process payment verification and update payment status
        
        Args:
            payment: Payment instance
        
        Returns:
            dict: Verification result
        """
        try:
            payment.verification_attempts += 1
            payment.last_verification_at = timezone.now()
            payment.save()
            
            verification_result = self.verify_payment(str(payment.payment_reference))
            
            if verification_result['success']:
                transaction_status = verification_result['status']
                payment.chapa_response.update(verification_result['data'])
                
                if transaction_status == 'success':
                    payment.mark_as_completed()
                    payment.webhook_verified = True
                    payment.save()
                    
                    return {
                        'success': True,
                        'status': 'completed',
                        'message': 'Payment completed successfully'
                    }
                elif transaction_status in ['failed', 'cancelled']:
                    payment.mark_as_failed(f'Payment {transaction_status}')
                    
                    return {
                        'success': False,
                        'status': transaction_status,
                        'message': f'Payment {transaction_status}'
                    }
                else:
                    # Payment still pending
                    payment.save()
                    
                    return {
                        'success': True,
                        'status': 'pending',
                        'message': 'Payment is still being processed'
                    }
            else:
                return {
                    'success': False,
                    'status': 'verification_failed',
                    'message': verification_result['error']
                }
                
        except Exception as e:
            logger.error(f"Error verifying payment {payment.payment_reference}: {str(e)}")
            return {
                'success': False,
                'status': 'error',
                'message': f'Verification error: {str(e)}'
            }
    
    def handle_webhook(self, webhook_data):
        """
        Handle Chapa webhook notifications
        
        Args:
            webhook_data (dict): Webhook payload from Chapa
        
        Returns:
            dict: Webhook processing result
        """
        try:
            tx_ref = webhook_data.get('tx_ref')
            status = webhook_data.get('status')
            
            if not tx_ref:
                return {
                    'success': False,
                    'message': 'Missing transaction reference'
                }
            
            try:
                payment = Payment.objects.get(payment_reference=tx_ref)
            except Payment.DoesNotExist:
                logger.error(f"Payment not found for tx_ref: {tx_ref}")
                return {
                    'success': False,
                    'message': 'Payment not found'
                }
            
            # Update payment with webhook data
            payment.chapa_response.update(webhook_data)
            
            if status == 'success':
                payment.mark_as_completed()
                payment.webhook_verified = True
                payment.save()
                
                return {
                    'success': True,
                    'message': 'Payment completed via webhook'
                }
            elif status in ['failed', 'cancelled']:
                payment.mark_as_failed(f'Webhook: Payment {status}')
                
                return {
                    'success': True,
                    'message': f'Payment {status} via webhook'
                }
            else:
                payment.save()
                
                return {
                    'success': True,
                    'message': 'Webhook processed, payment status updated'
                }
                
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            return {
                'success': False,
                'message': f'Webhook processing error: {str(e)}'
            }
