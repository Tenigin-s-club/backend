alembic upgrade head # apply migrations
# start fastapi app
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind="0.0.0.0:${FASTAPI_PORT}"
