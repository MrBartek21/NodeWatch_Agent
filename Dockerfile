FROM python:3.13-slim

# Ustawienie katalogu roboczego
WORKDIR /app

# Instalacja wymaganych pakietów systemowych
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        docker.io \
        docker-compose \
        curl \
        git \
        build-essential \
        libffi-dev \
        libssl-dev \
        python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Instalacja zależności Pythona
RUN pip install --no-cache-dir \
        requests \
        docker \
        python-dotenv \
        psutil \
        flask

# Kopiowanie kodu agenta
COPY . /app

# Ustawienia środowiska
ENV PYTHONUNBUFFERED=1 \
    FLASK_RUN_HOST=0.0.0.0 \
    FLASK_RUN_PORT=5000

# Uruchomienie agenta
CMD ["python", "agent.py"]
