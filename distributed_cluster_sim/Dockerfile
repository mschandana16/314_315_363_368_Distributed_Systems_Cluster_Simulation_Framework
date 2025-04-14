FROM python:3.9

WORKDIR /app
COPY node_simulator/node.py node.py
COPY requirements.txt .
RUN pip install -r requirements.txt

CMD ["python", "node.py"]
