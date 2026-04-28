FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir \
    fastapi uvicorn langchain langchain-openai langchain-community \
    langchain-core openai mysql-connector-python bcrypt pyjwt \
    python-multipart azure-storage-blob boto3 python-dotenv \
    tavily-python pydantic passlib requests

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
