FROM python:3.9-slim

WORKDIR /app

# Copy common library
COPY common/ /app/common/

# Copy service code
COPY services/restaurant-worker/app/ /app/
COPY services/restaurant-worker/requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the service
CMD ["python", "main.py"]
