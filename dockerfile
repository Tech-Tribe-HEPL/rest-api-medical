# Use the official Python image from Docker Hub
FROM python:3

# Set the working directory in the container
WORKDIR /app

# Copy just the requirements file first to leverage Docker cache
COPY requirements.txt /app

# Download repo to make available packages
RUN apt-get update

# Install dependency for the lib interacting with postgresql
RUN apt-get install -y libpq5

# Install dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the application code into the container
COPY . /app

EXPOSE 5000

# Run main.py when the container launches
CMD ["gunicorn", "--config", "gunicorn_config.py", "main:app"]
# Run the debug server
# CMD ["flask","--app","/app/main.py", "run", "--debug"]