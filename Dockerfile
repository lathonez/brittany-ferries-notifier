# Use official Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install system dependencies (for PyPDF2, requests, dotenv, no extra needed)
# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Set environment variables (optional, can be overridden at runtime)
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python", "main.py"]