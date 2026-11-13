FROM python:3.12-slim

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN pip install --no-cache-dir flask==3.1.1
RUN pip install --no-cache-dir git+https://github.com/rany2/edge-tts.git@master

COPY app.py .

EXPOSE 5100
CMD ["python", "app.py"]
