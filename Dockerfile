# Use Python 3.10
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port
EXPOSE 10000

# Start the app using gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:10000", "app:app"]
