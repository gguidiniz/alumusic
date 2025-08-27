import os
from celery import Celery, Task
from flask import Flask

celery_app = Celery(
    "worker",
    broker=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0"),
    result_backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0"),
    include=["app.tasks"]
)

def init_celery(app: Flask):
    celery_app.conf.update(app.config)

    class FlaskTask(Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app.Task = FlaskTask