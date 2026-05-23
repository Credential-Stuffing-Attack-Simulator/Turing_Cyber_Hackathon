FROM python:3.12-slim

LABEL description="Async credential stuffing attack engine — adversary simulation only"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/reports

ENV TARGET_URL=http://nginx/
ENV ATTACK_PROFILE=baseline
ENV ATTACK_ID=demo-baseline
ENV CREDENTIAL_FILE=configs/credentials.txt
ENV REPORT_DIR=/app/reports

CMD ["python", "main.py", "--allow-lab-host"]
