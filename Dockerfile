FROM python:3.11.4-bookworm

RUN apt-get update && apt-get install -y redis-server

WORKDIR /code

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8000

ENTRYPOINT ["bash", "start.sh"]
