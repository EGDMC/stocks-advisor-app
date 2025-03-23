# Use Python 3.9 to match Google Cloud Functions runtime
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements files
COPY requirements.txt .
COPY requirements_prod.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements_prod.txt

# Copy application code
COPY src/ ./src/
COPY data/ ./data/
COPY models/ ./models/

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_APP=src/app.py
ENV FLASK_ENV=development

# Expose port
EXPOSE 8080

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "src.app:server"]