# Use an official Python runtime as a parent image
FROM python:3.10-slim  

# Set the working directory in the container
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install any needed packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Define environment variable
ENV PYTHONUNBUFFERED=1
ENV MODE=production

# Run the application
CMD ["uvicorn", "Main:app", "--host", "0.0.0.0", "--port", "8000"]