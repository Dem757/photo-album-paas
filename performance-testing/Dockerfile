FROM python:3.11-slim

RUN pip install locust

WORKDIR /mnt/locust
COPY locustfile.py .

EXPOSE 8089

ENTRYPOINT ["locust", "-f", "locustfile.py"]