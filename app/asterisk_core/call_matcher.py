import asterisk.manager
import random
import time
from datetime import datetime
from app.models.call_schedule import CallSchedule
import threading
import logging
import sys

# Enhanced logging setup
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('call_matcher.log')
    ]
)
logger = logging.getLogger(__name__)

class CallMatcher:
    def __init__(self, ami_host='212.28.185.55', ami_port=5038, ami_username='asterisk_manager', ami_password='AsTrisk3923299'):
        self.manager = None
        self.ami_config = {
            'host': ami_host,
            'port': ami_port,
            'username': ami_username,
            'password': ami_password
        }
        logger.debug(f"Initializing CallMatcher with host: {ami_host}, port: {ami_port}")
        
    def connect_ami(self):
        """Establish connection to Asterisk AMI"""
        try:
            logger.debug("Attempting to connect to Asterisk AMI...")
            self.manager = asterisk.manager.Manager()
            
            logger.debug(f"Connecting to {self.ami_config['host']}:{self.ami_config['port']}")
            self.manager.connect(self.ami_config['host'], self.ami_config['port'])
            
            logger.debug("Connected. Attempting login...")
            self.manager.login(self.ami_config['username'], self.ami_config['password'])
            
            # Verify connection status
            if self.manager.connected():
                logger.info("Successfully connected to Asterisk AMI")
                # Get Asterisk version for verification
                response = self.manager.command('core show version')
                logger.debug(f"Asterisk Version: {response.data}")
                return True
            else:
                logger.error("Manager reports as not connected after login")
                return False
                
        except asterisk.manager.ManagerSocketException as e:
            logger.error(f"Socket Error connecting to Asterisk AMI: {e}")
            return False
        except asterisk.manager.ManagerAuthException as e:
            logger.error(f"Authentication failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to Asterisk AMI: {type(e).__name__} - {e}")
            return False

    def initiate_call(self, source_extension, destination_extension):
        """Initiate call between two extensions using Asterisk AMI"""
        try:
            logger.debug(f"Initiating call from {source_extension} to {destination_extension}")
            
            # Verify manager connection before proceeding
            if not self.manager or not self.manager.connected():
                logger.error("AMI manager not connected. Reconnecting...")
                if not self.connect_ami():
                    return False

            channel = f"PJSIP/{source_extension}"
            context = 'from-internal'
            extension = destination_extension
            priority = 1

            logger.debug(f"Originating call with channel: {channel}, context: {context}")
            
            originate_response = self.manager.originate(
                channel,
                extension,
                context=context,
                priority=priority,
                timeout=30000,
                variables={
                    'CALLER_ID_NUMBER': source_extension,
                    'MATCHED_EXTENSION': destination_extension
                }
            )
            
            logger.debug(f"Originate response: {originate_response}")
            return True
            
        except asterisk.manager.ManagerSocketException as e:
            logger.error(f"Socket Error during call initiation: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to initiate call: {type(e).__name__} - {e}")
            return False

    def match_and_connect_users(self, pending_calls):
        """Match users and initiate calls between them"""
        logger.debug(f"Starting matching process with {len(pending_calls)} pending calls")
        if not pending_calls:
            logger.debug("No pending calls to process")
            return

        available_users = [
            {
                'schedule_id': call['id'],
                'extension': call['source_extension']
            }
            for call in pending_calls
        ]
        
        logger.debug(f"Available users for matching: {available_users}")

        random.shuffle(available_users)
        logger.debug("Users shuffled for random matching")

        while len(available_users) >= 2:
            user1 = available_users.pop()
            user2 = available_users.pop()
            
            logger.debug(f"Attempting to match users: {user1['extension']} with {user2['extension']}")

            if self.initiate_call(user1['extension'], user2['extension']):
                logger.info(f"Successfully initiated call between {user1['extension']} and {user2['extension']}")
                CallSchedule.update_status(user1['schedule_id'], 'connected')
                CallSchedule.update_status(user2['schedule_id'], 'connected')
            else:
                logger.error(f"Failed to connect users {user1['extension']} and {user2['extension']}")
                CallSchedule.update_status(user1['schedule_id'], 'failed')
                CallSchedule.update_status(user2['schedule_id'], 'failed')

        if available_users:
            single_user = available_users[0]
            logger.info(f"Unpaired user remaining: {single_user['extension']}")
            CallSchedule.update_status(single_user['schedule_id'], 'no_match')

    def check_and_process_schedules(self):
        """Check for pending calls and process them"""
        try:
            logger.debug("Checking for pending calls...")
            pending_calls = CallSchedule.get_pending_calls()
            logger.debug(f"Found {len(pending_calls) if pending_calls else 0} pending calls")
            
            if pending_calls:
                self.match_and_connect_users(pending_calls)
        except Exception as e:
            logger.error(f"Error processing schedules: {type(e).__name__} - {e}")

    def run_scheduler(self, interval=60):
        """Run the scheduler continuously"""
        logger.info(f"Starting scheduler with {interval} second interval")
        while True:
            try:
                if not self.manager or not self.manager.connected():
                    logger.warning("AMI connection lost or not established. Reconnecting...")
                    self.connect_ami()
                
                logger.debug("Running schedule check cycle")
                self.check_and_process_schedules()
                
                logger.debug(f"Sleeping for {interval} seconds")
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {type(e).__name__} - {e}")
                time.sleep(5)  # Wait a bit before retrying

def main():
    logger.info("Starting Call Matcher application")
    matcher = CallMatcher()
    
    if matcher.connect_ami():
        try:
            logger.info("Starting scheduler thread")
            scheduler_thread = threading.Thread(target=matcher.run_scheduler)
            scheduler_thread.daemon = True
            scheduler_thread.start()

            logger.info("Main thread entering keep-alive loop")
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
            if matcher.manager:
                matcher.manager.close()
                logger.info("AMI connection closed")
    else:
        logger.error("Failed to start due to AMI connection failure")

if __name__ == "__main__":
    main()