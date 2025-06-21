FROM python:3.12.10-slim-bullseye

# Устанавливаем Java + Spark + Mongo-connector
# Устанавливаем Java и необходимые зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-17-jre-headless \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir pyspark==3.5.6 fastapi uvicorn pymongo[srv] numpy setuptools

RUN mkdir /app

WORKDIR /app
COPY service.py .


EXPOSE 12080
CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "12080"]
