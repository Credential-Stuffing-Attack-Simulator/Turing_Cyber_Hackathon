FROM python:3.12-slim

LABEL description="Telemetry dashboard — adversary simulation platform"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /var/log/lab /app/reports

ENV FLASK_APP=app.py
ENV LAB_DATA_DIR=/var/log/lab
ENV REPORT_DIR=/app/reports

EXPOSE 5001

HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5001/health')"

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5001"]
