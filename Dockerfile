# FROM python:3.11-slim

# WORKDIR /app

# COPY . .

# RUN pip install --no-cache-dir -r requirements.txt

# EXPOSE 8000

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]



FROM python:3.11-slim

# Install Redis server
RUN apt-get update && apt-get install -y redis-server && apt-get clean

# Set working directory
WORKDIR /app

# Copy your app code
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose FastAPI and Redis ports
EXPOSE 8000 6379

# Start both Redis server and FastAPI
CMD service redis-server start && uvicorn app.main:app --host 0.0.0.0 --port 8000
