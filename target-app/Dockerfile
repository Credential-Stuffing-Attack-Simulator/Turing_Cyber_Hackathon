FROM python:3.12-slim

LABEL maintainer="Credential Stuffing Attack Simulator"
LABEL description="Vulnerable Flask authentication target — adversary simulation only"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create required directories
RUN mkdir -p /var/log/lab /app/data

ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV LAB_DATA_DIR=/var/log/lab
ENV DB_PATH=/app/data/users.db
ENV DEFENSE_MODE=weak

EXPOSE 5000

HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
