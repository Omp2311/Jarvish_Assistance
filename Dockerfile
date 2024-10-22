# Use the official Python image as a base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container (Change /app to your project name)
WORKDIR /Jarvish_website

# Copy the requirements.txt file to the working directory
COPY requirements.txt /Jarvish_website/

# Install the required dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the entire project to the working directory
COPY . /Jarvish_website/

# Expose port 8000 for the Django app
EXPOSE 8000

# Run the Django development server
CMD ["python", "manage.py", "runserver", "127.0.0.1:8000"]
