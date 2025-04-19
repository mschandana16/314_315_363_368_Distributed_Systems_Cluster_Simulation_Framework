FROM python:3.9-slim

WORKDIR /app
COPY heartbeat_sender.py .

RUN pip install requests

CMD ["python", "heartbeat_sender.py"]
