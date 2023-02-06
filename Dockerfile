# Use an official Python image as the base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI application code to the container
COPY . .

# Set the environment variable for the FastAPI application
ENV PORT 80

# Run the FastAPI application
CMD ["uvicorn", "web_app:app", "--host", "0.0.0.0", "--port", "80"]

