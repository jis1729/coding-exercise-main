# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory in the container
WORKDIR /api

# Copy the current directory contents into the container at /app
COPY ./api/ /api
COPY requirements.txt requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run app.py when the container launches
CMD ["flask", "run", "--host=0.0.0.0"]