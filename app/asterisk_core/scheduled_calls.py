# app/models/scheduled_calls.py
from app.models.base_model import BaseModel

class ScheduledCalls(BaseModel):
    @classmethod
    def get_pending_calls(cls):
        """Get all pending calls that are due for execution"""
        query = """
        SELECT 
            id,
            user_id,
            source_extension,
            scheduled_time,
            status,
            notes,
            retry_count
        FROM scheduled_calls 
        WHERE status = 'pending' 
        AND scheduled_time <= NOW() 
        AND retry_count < 3
        """
        return cls.execute_query(query)

    @classmethod
    def update_call_status(cls, call_id, status, retry_count=None):
        """Update the status and retry count of a scheduled call"""
        query = """
        UPDATE scheduled_calls 
        SET 
            status = %s,
            retry_count = COALESCE(%s, retry_count),
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        """
        return cls.execute_update(query, (status, retry_count, call_id))


# asterisk-core/scheduler_service.py
import time
import threading
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


# Modified section of your run.py
"""
app = create_app()
CORS(app, ...)

# Initialize the scheduler
initialize_scheduler(app)

if __name__ == '__main__':
    app.run(host=host, port=port, debug=debug)
"""