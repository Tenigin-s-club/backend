FROM python:3.12-slim

WORKDIR /backend

# install project dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# copy project files
COPY . .

# run entrypoint script
RUN chmod 777 ./entrypoint.sh
RUN chmod 777 ./celery_build.sh
ENTRYPOINT ./entrypoint.sh
