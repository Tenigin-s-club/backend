#!/bin/bash 

# celery -A app.config:celery_client worker --loglevel=info
celery --app=app.config:celery_client worker -l INFO