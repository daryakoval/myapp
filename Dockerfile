# Use the official Python image as the base image
FROM python:3.11

# Install Redis server
RUN apt-get update && apt-get install -y redis-server

# Set the working directory inside the container
WORKDIR /app

# Copy the files code into the container
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

EXPOSE 8000

# Start Gunicorn to run the Flask application
CMD ["bash", "start.sh"]
