from apscheduler.schedulers.background import BackgroundScheduler
from app.services.call_scheduler_service import CallSchedulerService

def init_scheduler(app):
    scheduler = BackgroundScheduler()
    call_service = CallSchedulerService()

    @scheduler.scheduled_job('interval', minutes=1)
    def schedule_calls():
        with app.app_context():
            call_service.process_pending_calls()

    scheduler.start()