FROM python:3.9-slim

WORKDIR /app

# Copy common library
COPY common/ /app/common/

# Copy service code
COPY services/restaurant-api/app/ /app/
COPY services/restaurant-api/requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8002

# Run the service
CMD ["python", "main.py"]
