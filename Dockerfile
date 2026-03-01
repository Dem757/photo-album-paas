FROM python:3.12-slim

# Környezeti változók a Pythonhoz
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Munkakönyvtár létrehozása
WORKDIR /app

# Függőségek telepítése
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# A kód másolása
COPY . /app/

# Port megnyitása (OpenShift/OKD alapértelmezettje a 8080)
EXPOSE 8080

# Az alkalmazás indítása Gunicorn-nal
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "core.wsgi:application"]