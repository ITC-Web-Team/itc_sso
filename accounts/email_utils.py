import threading
from django.core.mail import EmailMessage
from django.conf import settings
import random
import logging
import time
import warnings

logger = logging.getLogger(__name__)

class EmailSender:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(EmailSender, cls).__new__(cls)
                    cls._instance._current_config_index = 0
                    cls._instance._config_failure_count = [0] * len(settings.EMAIL_CONFIGS)
        return cls._instance
    
    def _rotate_email_config(self):
        """
        Rotate to the next email configuration in a round-robin manner,
        with a fallback mechanism for failed configurations.
        """
        total_configs = len(settings.EMAIL_CONFIGS)
        
        # Find the next available configuration
        for _ in range(total_configs):
            self._current_config_index = (self._current_config_index + 1) % total_configs
            
            # Reset failure count if it exceeds a threshold
            if self._config_failure_count[self._current_config_index] > 3:
                self._config_failure_count[self._current_config_index] = 0
            
            # If the configuration hasn't failed too many times, use it
            if self._config_failure_count[self._current_config_index] < 3:
                break
        
        config = settings.EMAIL_CONFIGS[self._current_config_index]
        
        # Update Django's email settings dynamically
        from django.conf import settings as django_settings
        django_settings.EMAIL_HOST = config['EMAIL_HOST']
        django_settings.EMAIL_PORT = config['EMAIL_PORT']
        django_settings.EMAIL_USE_TLS = config['EMAIL_USE_TLS']
        django_settings.EMAIL_HOST_USER = config['EMAIL_HOST_USER']
        django_settings.EMAIL_HOST_PASSWORD = config['EMAIL_HOST_PASSWORD']
    
    def send_email(self, subject, message, recipient_list, html_message=None, max_attempts=3):
        """
        Send an email with automatic retry and email configuration rotation.
        
        :param subject: Email subject
        :param message: Plain text message
        :param recipient_list: List of recipient email addresses
        :param html_message: Optional HTML message
        :param max_attempts: Maximum number of send attempts
        :return: Boolean indicating success or failure
        """
        # Check if email configuration is available
        if not settings.EMAIL_CONFIGS or not settings.EMAIL_CONFIGS[0]['EMAIL_HOST_USER']:
            warnings.warn("Email sending is disabled due to missing configuration.", UserWarning)
            logger.warning(f"Failed to send email to {recipient_list}: No email configuration")
            return False

        total_configs = len(settings.EMAIL_CONFIGS)
        
        for attempt in range(max_attempts * total_configs):
            try:
                # Rotate email configuration for each attempt
                self._rotate_email_config()
                
                # Create email message
                email = EmailMessage(
                    subject=subject,
                    body=message,
                    from_email=settings.EMAIL_CONFIGS[self._current_config_index]['EMAIL_HOST_USER'],
                    to=recipient_list
                )
                
                # Attach HTML content if provided
                if html_message:
                    email.content_subtype = "html"
                    email.body = html_message
                
                # Send the email
                email.send()
                
                # Reset failure count for this configuration
                self._config_failure_count[self._current_config_index] = 0
                
                logger.info(f"Email sent successfully to {recipient_list}")
                return True
            
            except Exception as e:
                # Increment failure count for this configuration
                self._config_failure_count[self._current_config_index] += 1
                
                logger.error(f"Email send attempt {attempt + 1} failed: {str(e)}")
                
                # Add a small delay between attempts to prevent rapid retries
                time.sleep(2)
                
                # If all configurations have been tried multiple times, give up
                if attempt == (max_attempts * total_configs - 1):
                    logger.error(f"Failed to send email to {recipient_list} after {max_attempts * total_configs} attempts")
                    return False
        
        return False

# Convenience function for easy email sending
def send_email(subject, message, recipient_list, html_message=None):
    """
    Convenience wrapper for EmailSender
    """
    email_sender = EmailSender()
    return email_sender.send_email(subject, message, recipient_list, html_message) 