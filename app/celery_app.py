from celery import Celery, Task
from celery.schedules import crontab
from flask import Flask
import os

celery_app = Celery(
    "worker",
    broker=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0"),
    result_backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0"),
    include=["app.tasks"]
)

def init_celery(app: Flask):
    celery_app.conf.update(app.config.get("CELERY", {}))

    class FlaskTask(Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app.Task = FlaskTask
    app.extensions["celery"] = celery_app

celery_app.conf.beat_schedule = {
    'generate-weekly-summary-every-sunday': {
        'task': 'app.tasks.generate_weekly_summary',
        'schedule': crontab(hour=1, minute=0, day_of_week='sunday'),
    },
}