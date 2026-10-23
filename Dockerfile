FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install the libraries first. Docker remembers this step, so rebuilding after a code change is fast.
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy the app: the backend and the frontend pages.
COPY backend backend
COPY frontend frontend

# Run as a normal user, not as root, which is safer.
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

WORKDIR /app/backend
ENV PORT=8000
EXPOSE 8000

# Hosts such as Render give the port in $PORT. --proxy-headers lets the rate limits see the
# visitor's real address instead of the host's proxy.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --proxy-headers --forwarded-allow-ips='*'"]