# Codeingo code runner (C, C++, Java). Deploy as its OWN service: it holds no database or user data, and runs
# strangers' programs. Runs as root ONLY so it can start each program as the unprivileged user "nobody" (and, where
# the host allows, with no network); the programs themselves never run as root.
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc g++ libc6-dev default-jdk-headless util-linux \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /srv
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
EXPOSE 8000
# one worker: each request already runs its program in a subprocess, and the free tier has a fraction of a CPU
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--no-server-header"]
