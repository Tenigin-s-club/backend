# celery -A app.config:celery_client worker --loglevel=info
alembic upgrade head # apply migrations
# start fastapi app
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind="0.0.0.0:${FASTAPI_PORT}" &
# start autobooking
# uvicorn app.main:app --reload &
echo "piradas"
sleep 5
echo "huesos"
python3 autobooking.py &
echo "eblan"
wait
