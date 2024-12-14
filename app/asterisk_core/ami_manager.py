# asterisk-core/ami_manager.py
import socket
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AsteriskAMI:
    def __init__(self, host='localhost', port=5038, username='admin', secret='password'):
        self.host = host
        self.port = port
        self.username = username
        self.secret = secret
        self.socket = None

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            return self.login()
        except Exception as e:
            logger.error(f"AMI Connection failed: {str(e)}")
            return False

    def login(self):
        login_str = (
            f"Action: Login\r\n"
            f"Username: {self.username}\r\n"
            f"Secret: {self.secret}\r\n"
            f"Events: off\r\n\r\n"
        )
        try:
            self.socket.send(login_str.encode())
            response = self.receive()
            return "Success" in response
        except Exception as e:
            logger.error(f"AMI Login failed: {str(e)}")
            return False

    def originate_call(self, extension):
        command = (
            f"Action: Originate\r\n"
            f"Channel: SIP/{extension}\r\n"
            f"Context: default\r\n"
            f"Exten: {extension}\r\n"
            f"Priority: 1\r\n"
            f"Async: yes\r\n\r\n"
        )
        try:
            self.socket.send(command.encode())
            response = self.receive()
            return "Success" in response
        except Exception as e:
            logger.error(f"Call origination failed: {str(e)}")
            return False

    def receive(self, timeout=2):
        self.socket.settimeout(timeout)
        response = ""
        try:
            while True:
                chunk = self.socket.recv(4096).decode()
                response += chunk
                if response.endswith("\r\n\r\n"):
                    break
        except socket.timeout:
            pass
        return response

    def close(self):
        if self.socket:
            self.socket.close()
