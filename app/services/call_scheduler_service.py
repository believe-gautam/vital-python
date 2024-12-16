import asterisk.manager
from datetime import datetime
from app.models.call_schedule import CallSchedule
from app.utils.logger import Logger
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CallSchedulerService:
    def __init__(self):
        self.manager = None
        # Get AMI credentials from environment variables
        self.ami_host = os.getenv('AMI_HOST', 'localhost')
        self.ami_port = int(os.getenv('AMI_PORT', 5038))
        self.ami_username = os.getenv('AMI_USERNAME')
        self.ami_password = os.getenv('AMI_PASSWORD')
        Logger.info(f"CallSchedulerService initialized with host: {self.ami_host}, port: {self.ami_port}")

    def connect_ami(self):
        try:
            Logger.info(f"Attempting to connect to AMI at {self.ami_host}:{self.ami_port}")
            self.manager = asterisk.manager.Manager()
            self.manager.connect(host=self.ami_host, port=self.ami_port)
            
            Logger.info("AMI connection established, attempting login...")
            self.manager.login(username=self.ami_username, secret=self.ami_password)
            
            Logger.info("Successfully logged in to AMI")
            return True
        except asterisk.manager.ManagerSocketException as e:
            Logger.error(f"AMI Socket Connection Error: {str(e)}")
            return False
        except asterisk.manager.ManagerAuthException as e:
            Logger.error(f"AMI Authentication Error: {str(e)}")
            return False
        except Exception as e:
            Logger.error(f"Unexpected AMI Connection Error: {str(e)}")
            return False

    def initiate_call(self, source_extension):
        """Initiate call from source extension"""
        try:
            Logger.info(f"Fetching pending calls for extension: {source_extension}")
            available_extensions = CallSchedule.get_pending_calls()
            Logger.info(f"Found {len(available_extensions)} pending calls")

            potential_partners = [
                call for call in available_extensions 
                if call['source_extension'] != source_extension
            ]
            Logger.info(f"Found {len(potential_partners)} potential partners for extension {source_extension}")

            if not potential_partners:
                Logger.warning(f"No available partners for extension {source_extension}")
                CallSchedule.update_status(source_extension, 'no_partner')
                return False

            partner = potential_partners[0]
            Logger.info(f"Selected partner extension: {partner['source_extension']}")

            Logger.info(f"Initiating call from {source_extension} to {partner['source_extension']}")
            self.manager.originate(
                channel=f'SIP/{source_extension}',
                exten=partner['source_extension'],
                context='from-internal',
                priority=1,
                timeout=30000,
                caller_id=f'Scheduled Call <{source_extension}>'
            )

            Logger.info(f"Updating status for extension {source_extension} to 'in_progress'")
            CallSchedule.update_status(source_extension, 'in_progress')
            
            Logger.info(f"Updating status for extension {partner['id']} to 'in_progress'")
            CallSchedule.update_status(partner['id'], 'in_progress')

            Logger.info(f"Successfully initiated call between {source_extension} and {partner['source_extension']}")
            return True

        except Exception as e:
            Logger.error(f"Call initiation error for extension {source_extension}: {str(e)}")
            current_call = CallSchedule.get_by_id(source_extension)
            if current_call:
                new_retry_count = (current_call.get('retry_count') or 0) + 1
                Logger.info(f"Updating retry count for extension {source_extension} to {new_retry_count}")
                CallSchedule.update_status(source_extension, 'failed', new_retry_count)
            return False

    def process_pending_calls(self):
        """Process all pending calls"""
        try:
            Logger.info("Starting to process pending calls...")
            
            if not self.connect_ami():
                Logger.error("Failed to connect to AMI, aborting call processing")
                return False

            Logger.info("Fetching pending calls...")
            pending_calls = CallSchedule.get_pending_calls()
            
            if not pending_calls:
                Logger.info("No pending calls to process")
                return True

            Logger.info(f"Found {len(pending_calls)} pending calls to process")
            
            processed_extensions = set()
            successful_calls = 0
            failed_calls = 0

            for call in pending_calls:
                source_extension = call['source_extension']
                
                if source_extension in processed_extensions:
                    Logger.info(f"Extension {source_extension} already processed, skipping")
                    continue

                Logger.info(f"Processing call for extension {source_extension}")
                if self.initiate_call(call['id']):
                    processed_extensions.add(source_extension)
                    successful_calls += 1
                else:
                    failed_calls += 1

            Logger.info(f"Call processing completed. Successful: {successful_calls}, Failed: {failed_calls}")
            return True

        except Exception as e:
            Logger.error(f"Error in process_pending_calls: {str(e)}")
            return False
        finally:
            if self.manager:
                Logger.info("Closing AMI connection")
                self.manager.close()