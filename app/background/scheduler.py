# app/background/scheduler.py
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.call_scheduler import CallScheduler

def init_scheduler(app: Flask):
    scheduler = BackgroundScheduler()
    call_scheduler = CallScheduler()

    @scheduler.scheduled_job('interval', minutes=1)
    def schedule_calls():
        with app.app_context():
            call_scheduler.process_scheduled_calls()

    scheduler.start()

    