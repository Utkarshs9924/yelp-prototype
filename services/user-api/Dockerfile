FROM python:3.9-slim

WORKDIR /app

# Copy common library
COPY common/ /app/common/

# Copy service code
COPY services/user-api/app/ /app/
COPY services/user-api/requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8001

# Run the service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "4", "--timeout-keep-alive", "120"]
