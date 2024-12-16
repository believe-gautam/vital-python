import asterisk.manager

def connect_asterisk():
    try:
        # Create manager instance
        manager = asterisk.manager.Manager()
        
        # Connect to Asterisk server
        manager.connect('localhost')  # Use your server IP if not local
        
        # Login with credentials from manager.conf
        manager.login('myuser', 'mypassword')
        
        print("Successfully connected to Asterisk")
        return manager
        
    except asterisk.manager.ManagerSocketException:
        print("Unable to connect to Asterisk server. Check if Asterisk is running.")
        return None
    except asterisk.manager.ManagerAuthException:
        print("Authentication failed. Check username/password.")
        return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

# Simple test to verify connection
def test_connection():
    manager = connect_asterisk()
    if manager:
        # Get Asterisk version - simple test command
        response = manager.command('core show version')
        print(response.data)
        
        # Close the connection
        manager.close()
        print("Connection closed")

# Run the test
if __name__ == "__main__":
    test_connection()