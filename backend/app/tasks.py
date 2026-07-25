from celery import Celery
import os

# Initialize a basic Celery app so the worker container doesn't crash on startup.
# We will fully configure this in later milestones when we build background jobs.
celery = Celery(
    'ai_gateway',
    broker=os.getenv('REDIS_URL', 'redis://redis:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://redis:6379/0')
)
