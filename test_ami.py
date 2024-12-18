# import asterisk.manager
# import os
# from dotenv import load_dotenv
# from app.utils.logger import Logger

# # Load environment variables
# load_dotenv()

# def test_ami_connection():
#     try:
#         # Get AMI credentials from environment variables
#         ami_host = os.getenv('AMI_HOST', 'localhost')
#         ami_port = int(os.getenv('AMI_PORT', 5038))
#         ami_username = os.getenv('AMI_USERNAME')
#         ami_password = os.getenv('AMI_PASSWORD')

#         Logger.info(f"Testing AMI connection with following details:")
#         Logger.info(f"Host: {ami_host}")
#         Logger.info(f"Port: {ami_port}")
#         Logger.info(f"Username: {ami_username}")

#         # Create manager instance
#         manager = asterisk.manager.Manager()
        
#         # Connect to AMI
#         Logger.info("Attempting to connect to AMI...")
#         manager.connect(host=ami_host, port=ami_port)
#         Logger.info("Successfully connected to AMI")
        
#         # Login to AMI
#         Logger.info("Attempting to login...")
#         manager.login(username=ami_username, secret=ami_password)
#         Logger.info("Successfully logged in to AMI")

#         # Test a simple command
#         Logger.info("Testing AMI command...")
#         response = manager.command('core show version')
#         Logger.info(f"Asterisk Version Response: {response.data}")

#         # Close connection
#         manager.close()
#         Logger.info("AMI connection test completed successfully")
#         return True

#     except asterisk.manager.ManagerSocketException as e:
#         Logger.error(f"Unable to connect to Asterisk server: {e}")
#         Logger.error("Please check if:")
#         Logger.error("- Asterisk is running")
#         Logger.error("- Manager interface is enabled")
#         Logger.error("- Connection details (host/port) are correct")
#         return False
        
#     except asterisk.manager.ManagerAuthException as e:
#         Logger.error(f"Authentication failed: {e}")
#         Logger.error("Please verify your username and password in manager.conf")
#         return False
        
#     except Exception as e:
#         Logger.error(f"Unexpected error: {e}")
#         return False

# if __name__ == "__main__":
#     test_ami_connection()


import asterisk.manager

def connect_asterisk():
    try:
        # AMI connection details
        ami_host = '212.28.185.55'  # or your Asterisk server IP
        ami_port = 5038        # Default AMI port
        ami_user = 'asterisk_manager'    # Your AMI username from manager.conf
        ami_pass = 'AsTrisk3923299' # Your AMI password from manager.conf

        # Create manager instance
        manager = asterisk.manager.Manager()
        
        # Connect with port specified
        manager.connect(host=ami_host, port=ami_port)
        
        # Login
        manager.login(username=ami_user, secret=ami_pass)
        
        print("Successfully connected to Asterisk AMI")
        
        # Test the connection with a simple command
        response = manager.command('core show version')
        print("Asterisk Version:", response.data)
        
        return manager

    except asterisk.manager.ManagerSocketException as socket_error:
        print(f"Unable to connect to Asterisk server: {socket_error}")
        print("Please check if:")
        print("- Asterisk is running")
        print("- Manager interface is enabled")
        print("- Connection details (host/port) are correct")
        return None
        
    except asterisk.manager.ManagerAuthException as auth_error:
        print(f"Authentication failed: {auth_error}")
        print("Please verify your username and password in manager.conf")
        return None
        
    except Exception as e:
        print(f"Unexpected error occurred: {str(e)}")
        return None

# Simple test to verify connection
def test_connection():
    manager = connect_asterisk()
    if manager:
        try:
            # Additional test commands can be added here
            print("\nConnection test successful!")
            
        finally:
            # Always close the connection
            manager.close()
            print("Connection closed")

if __name__ == "__main__":
    test_connection()