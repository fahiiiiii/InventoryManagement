# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /code

# Copy the project requirements into the container
COPY requirements.txt /code/

# Install project dependencies
RUN pip install --no-cache-dir -r requirements.txt 


RUN apt-get update && apt-get install -y libgdal-dev python3-gdal gdal-bin

# Copy the rest of the application code
COPY . /code/

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
