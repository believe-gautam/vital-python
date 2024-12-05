# app/services/asterisk_service.py
import os
from asterisk.manager import Manager, ManagerSocketException
import logging

class AsteriskService:
    def __init__(self):
        self.manager = None
        # Don't connect immediately
        self._connected = False

    def ensure_connected(self):
        """Ensure connection is established before performing operations"""
        if not self._connected:
            try:
                self.connect()
            except Exception as e:
                logging.error(f"Failed to connect to Asterisk AMI: {str(e)}")
                raise

    def connect(self):
        """Establish connection to Asterisk AMI"""
        try:
            if self.manager:
                self.manager.close()
            
            self.manager = Manager()
            self.manager.connect(
                host=os.getenv('AMI_HOST', 'localhost'),
                port=int(os.getenv('AMI_PORT', 5038))
            )
            self.manager.login(
                username=os.getenv('AMI_USERNAME', 'api_user'),
                secret=os.getenv('AMI_PASSWORD', 'your_secure_password')
            )
            self._connected = True
        except Exception as e:
            self._connected = False
            logging.error(f"Failed to connect to Asterisk AMI: {str(e)}")
            raise

    def originate_call(self, caller, destination):
        """Originate a call with connection check"""
        try:
            self.ensure_connected()
            
            response = self.manager.originate(
                channel=f'PJSIP/{caller}',
                exten=destination,
                context='testing',
                priority=1,
                timeout=30000
            )
            return response
        except Exception as e:
            logging.error(f"Failed to originate call: {str(e)}")
            self._connected = False  # Reset connection state
            raise

    def __del__(self):
        """Clean shutdown of manager connection"""
        try:
            if self.manager and self._connected:
                self.manager.close()
        except:
            pass  # Suppress errors during shutdown