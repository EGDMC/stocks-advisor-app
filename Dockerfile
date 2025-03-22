# Use Python 3.9 slim base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY src/ ./src/
COPY vercel-deploy/api/ ./api/

# Set environment variables
ENV PYTHONPATH="/app"
ENV PORT=8080

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "src/app.py"]