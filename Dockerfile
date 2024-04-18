FROM python:3.12-slim

WORKDIR /app

COPY *.py /app
COPY requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]