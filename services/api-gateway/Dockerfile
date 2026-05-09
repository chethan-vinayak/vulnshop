FROM python:3.9-slim

# WARNING: Intentionally vulnerable microservice

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Intentionally vulnerable: running as root
USER root

# Expose port
EXPOSE 8080

# No health check - vulnerability
CMD ["python", "gateway.py"]
