FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app ./app
# Run as an unprivileged user
RUN useradd --system --uid 10001 --no-create-home codeingo
USER 10001
# One worker by default: small hosts (e.g. Render free: 0.1 CPU / 512 MB) start much faster and don't race to seed the
# database. Uvicorn reads WEB_CONCURRENCY itself - set it to 2+ on a bigger machine.
ENV WEB_CONCURRENCY=1
EXPOSE 8000
# The API port is only reachable on the private docker network (behind nginx), so trusting
# X-Forwarded-For from any peer there is safe. Bounded concurrency + short keep-alive limit abuse.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", \
     "--proxy-headers", "--forwarded-allow-ips", "*", "--no-server-header", \
     "--timeout-keep-alive", "5", "--limit-concurrency", "200", "--h11-max-incomplete-event-size", "16384"]
