FROM python:3.9-slim

WORKDIR /app

# Copy common library
COPY common/ /app/common/

# Copy service code
COPY services/user-worker/app/ /app/
COPY services/user-worker/requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the service
CMD ["python", "main.py"]
