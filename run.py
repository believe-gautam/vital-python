from app import create_app
import os
from dotenv import load_dotenv
from flask_cors import CORS
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from app.asterisk_core.call_matcher import CallMatcher
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Create Flask app
app = create_app()

# Initialize CallMatcher
call_matcher = CallMatcher()
scheduler = None

def init_call_matcher():
    """Initialize and start the call matcher background process"""
    global scheduler
    try:
        logger.info("Initializing call matcher...")
        if call_matcher.connect_ami():
            scheduler = BackgroundScheduler()
            # Run matching process every minute
            scheduler.add_job(
                func=call_matcher.check_and_process_schedules,
                trigger="interval",
                seconds=60,
                id='call_matcher_job'
            )
            scheduler.start()
            logger.info("Call matcher scheduler started successfully")
            return True
        else:
            logger.error("Failed to connect to AMI")
            return False
    except Exception as e:
        logger.error(f"Error initializing call matcher: {e}")
        return False

def cleanup_scheduler():
    """Cleanup function to shut down the scheduler"""
    global scheduler
    if scheduler:
        logger.info("Shutting down scheduler...")
        scheduler.shutdown()
        logger.info("Scheduler shutdown complete")

# Register cleanup function
atexit.register(cleanup_scheduler)

# Initialize CORS
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

@app.before_request
def before_request():
    """Initialize call matcher before first request if not already initialized"""
    global scheduler
    if not scheduler:
        init_call_matcher()

# Health check endpoint
@app.route('/health')
def health_check():
    """Health check endpoint to verify scheduler status"""
    global scheduler
    return {
        'status': 'healthy',
        'scheduler_running': bool(scheduler and scheduler.running)
    }

if __name__ == '__main__':
    # Get values from environment variables
    host = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_RUN_PORT', 3001))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Initialize call matcher before running the app
    init_call_matcher()
    
    logger.info(f"Starting Flask app on {host}:{port} (debug: {debug})")
    app.run(host=host, port=port, debug=debug)