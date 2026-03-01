# Photo Album PaaS - Django & OKD Project

This is a multi-tier, scalable web application designed for uploading and organizing photos into a gallery. The project demonstrates PaaS-based (OKD/OpenShift) application management, automated build pipelines, and persistent cloud storage.

---

## 🏗 Architecture (Multi-tier)

Following modern cloud-native principles, the application is divided into four distinct layers:

| Tier | Description |
|---|---|
| **Presentation Tier** | Powered by the Gunicorn WSGI server. Static file delivery is handled by WhiteNoise, ensuring CSS and JS are served efficiently without a separate Nginx container. |
| **Application Tier (Logic)** | A Django framework application running in a specialized Docker container. |
| **Data Tier** | A standalone PostgreSQL 18 container providing robust, structured data storage. |
| **Storage Tier** | A Persistent Volume Claim (PVC) ensures that uploaded media files remain intact across container restarts and redeployments. |

---

## 🚀 Deployment and Build Process

The application is hosted on the **OKD** (Origin Community Distribution of Kubernetes) platform.

### 1. Automated CI/CD (Webhooks)

The project is integrated with GitHub. Upon every `git push`, OKD automatically:

- Triggers a new build via **GitHub Webhooks**.
- Builds a new image based on the provided `Dockerfile` (**DockerStrategy**).
- Executes automated database migrations (`python manage.py migrate`).
- Performs a **Rolling Update** to replace old instances with the new version without downtime.

### 2. Dockerfile Strategy

To ensure environment independence and bypass internal OKD Builder Image limitations, a custom `Dockerfile` is used:

- **Base Image:** `python:3.12-slim` for a lightweight footprint.
- **Database Driver:** `psycopg2-binary` for reliable PostgreSQL communication.
- **Execution:** Automated migration scripts are bundled into the container startup command.

---

## ⚙️ Configuration (Environment Variables)

Sensitive data and inter-tier connections are managed via OKD Environment Variables:

| Variable | Description |
|---|---|
| `DATABASE_URL` | Connection string for PostgreSQL (user, pass, host, db). |
| `ALLOWED_HOSTS` | Security filter for the OKD route (set to `*` or specific domain). |
| `CSRF_TRUSTED_ORIGINS` | Trusted origins for secure SSL/HTTPS form submissions. |
| `SECURE_PROXY_SSL_HEADER` | Tells Django the request is secure (HTTPS) despite the SSL proxy. |

---

## 📈 Scalability and Persistence

### Horizontal Scalability

Because the application is **Stateless** (storing data and files in separate tiers), it can be scaled horizontally. The number of Pods can be increased at any time; the OKD Service will automatically load-balance traffic between them.

### Persistent Storage

Uploaded photos are stored in the `/app/media` directory, which is mounted to a **1GiB Persistent Volume Claim**. This prevents data loss during container restarts or build updates, solving the ephemeral file system limitation of standard containers.
