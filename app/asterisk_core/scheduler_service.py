# asterisk-core/scheduler_service.py
import time
import logging
from app.asterisk_core.scheduled_calls import ScheduledCalls
from .ami_manager import AsteriskAMI

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self, ami_config):
        self.ami = AsteriskAMI(**ami_config)
        self.running = False
        self.check_interval = 10  # seconds

    def start(self):
        self.running = True
        if not self.ami.connect():
            logger.error("Failed to connect to Asterisk AMI")
            return
        else:
            print("Connected to Asterisk AMI")


        while self.running:
            try:
                # Get pending calls from the database
                pending_calls = ScheduledCalls.get_pending_calls()
                
                for call in pending_calls:
                    logger.info(f"Processing call for extension {call['source_extension']}")
                    
                    # Attempt to make the call
                    success = self.ami.originate_call(call['source_extension'])
                    
                    if success:
                        ScheduledCalls.update_call_status(call['id'], 'completed')
                        logger.info(f"Call completed for extension {call['source_extension']}")
                    else:
                        new_retry_count = call['retry_count'] + 1
                        status = 'failed' if new_retry_count >= 3 else 'pending'
                        ScheduledCalls.update_call_status(
                            call['id'], 
                            status, 
                            new_retry_count
                        )
                        logger.warning(
                            f"Call failed for extension {call['source_extension']}, "
                            f"retry count: {new_retry_count}"
                        )
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Error in scheduler service: {str(e)}")
                time.sleep(self.check_interval)

    def stop(self):
        self.running = False
        self.ami.close()
