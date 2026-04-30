FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir \
    fastapi uvicorn "langchain==0.2.16" "langchain-openai==0.1.23" "langchain-community==0.2.16" \
    "langchain-core==0.2.38" openai mysql-connector-python bcrypt pyjwt \
    python-multipart azure-storage-blob boto3 python-dotenv \
    tavily-python pydantic passlib requests numpy pymongo dnspython

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]