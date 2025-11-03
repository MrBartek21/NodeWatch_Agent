FROM python:3.13-slim

WORKDIR /app

# Instalacja Dockera CLI i zależności
RUN apt-get update && apt-get install -y docker.io docker-compose curl && \
    pip install requests docker python-dotenv psutil && \
    rm -rf /var/lib/apt/lists/*

COPY . /app

ENV PYTHONUNBUFFERED=1

CMD ["python", "agent.py"]
