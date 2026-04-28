FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir \
    fastapi uvicorn "langchain==0.1.20" "langchain-openai==0.1.8" "langchain-community==0.0.38" \
    "langchain-core==0.1.52" openai mysql-connector-python bcrypt pyjwt \
    python-multipart azure-storage-blob boto3 python-dotenv \
    tavily-python pydantic passlib requests

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]