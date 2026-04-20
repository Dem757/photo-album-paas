# Photo Album PaaS Application

This project is a multi-tier web application designed for a Cloud Network Services laboratory environment (BMEVITMMB11). The application is built using the Django framework and is deployed on the OKD (Origin Community Distribution of Kubernetes) platform at fured.cloud.bme.hu.

## Architectural Overview

The application follows a cloud-native, multi-tier architecture to ensure separation of concerns, scalability, and data persistence.

### 1. Presentation and Application Tier
- **Framework:** Django
- **WSGI Server:** Gunicorn
- **Static Files:** WhiteNoise is integrated to serve static assets directly through the application server, eliminating the need for a separate Nginx container in this PaaS environment.
- **Security:** Configured to handle SSL termination at the OKD Route level with trusted host/origin settings.

### 2. Database Tier
- **Engine:** PostgreSQL 18
- **Deployment:** A standalone containerized database service.
- **Connectivity:** The application connects to the database via an internal Service DNS name, using environment variables for authentication.

### 3. Storage and Persistence Tier
- **Media Storage:** A 1GiB Persistent Volume Claim (PVC) is mounted at `/app/media` to ensure that uploaded photographs are preserved across container restarts and redeployments.
- **Database Persistence:** A separate 1GiB PVC is mounted at `/var/lib/postgresql` for the PostgreSQL service to ensure data integrity and persistence.

## Deployment and CI/CD

The deployment process is automated by GitHub Actions and Terraform.

- **Pipeline file:** `.github/workflows/deploy.yml`
- **Trigger:** Push to `main`
- **Terraform provider:** `hashicorp/kubernetes`
- **Target namespace:** `photo-album`

### CI/CD Workflow Summary
1. Checkout repository.
2. Run `terraform init` in `terraform/`.
3. Import already-existing cluster resources into Terraform state (`postgres-pvc`, `media-pvc`, services, deployments).
4. Run `terraform apply -auto-approve`.
5. Create or update the OpenShift Route with `kubectl apply`.
6. Restart Django deployment and wait for rollout status.
7. Run Django migrations inside a running Django pod with retry logic.

### Why Route Is Managed By kubectl
OpenShift Route management is done in the workflow (not Terraform manifest resources) to avoid CRD discovery/RBAC issues in restricted cluster contexts.

### Container Runtime Behavior
- Base image: `python:3.12-slim`
- App process: Gunicorn on `0.0.0.0:8080`
- Startup command runs migrations before serving traffic:
	- `python manage.py migrate --noinput && gunicorn --bind 0.0.0.0:8080 core.wsgi:application`

## Configuration

The Terraform deployment is parameterized with the following variables:

| Variable | Purpose |
|---|---|
| `okd_host` | OKD API endpoint (for Terraform Kubernetes provider). |
| `okd_token` | OKD token used by Terraform provider. |
| `db_password` | PostgreSQL password used by DB and Django connection URL. |
| `django_image` | Fully qualified image reference used by Django deployment. |
| `namespace` | Kubernetes/OKD namespace to deploy into (default: `photo-album`). |

The Django deployment uses environment variables:

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Defines the connection parameters for the PostgreSQL instance. |
| `ALLOWED_HOSTS` | Security filter for the OKD Route domain and internal service names. |
| `CSRF_TRUSTED_ORIGINS` | Ensures secure form submissions over HTTPS. |

## Implemented Kubernetes Resources

Defined in `terraform/main.tf`:
- `kubernetes_persistent_volume_claim_v1.postgres_pvc`
- `kubernetes_persistent_volume_claim_v1.media_pvc`
- `kubernetes_service_v1.postgres_svc`
- `kubernetes_service_v1.django_svc`
- `kubernetes_deployment_v1.postgres`
- `kubernetes_deployment_v1.django`

Notes:
- Django deployment uses `image_pull_policy = "Always"`.
- Django deployment sets `wait_for_rollout = false`; rollout checks are handled explicitly by the workflow with `kubectl rollout status`.

## Management Commands
Administrative tasks can be performed via the OKD Pod Terminal:
- **Create Administrative User:** `python manage.py createsuperuser`
- **Manual Migration:** `python manage.py migrate`

## Operational Notes and Troubleshooting

- If Terraform state is empty but resources already exist in the cluster, the import step in the workflow prevents `already exists` failures.
- Migration execution in CI uses retries and only targets running Django pods to avoid rollout race conditions.
- OpenShift SCC restrictions may reject hardcoded pod security context values (for example fixed `fsGroup`). Keep deployment security context aligned with namespace SCC policy.

## Performance Testing

Load testing assets are located in `performance-testing/` and are executed with Locust.

### Simulated User Behavior
The current Locust scenario (`performance-testing/locustfile.py`) simulates:
- Gallery browsing (`/`)
- Login page access (`/accounts/login/`)
- Sorted gallery views (`/?sort=...`)
- Authenticated photo upload (`/upload/`) with multipart image data

Each virtual user establishes an authenticated session in `on_start`.

### Authenticated Upload Test Modes
Two modes are supported for login credentials:
- **Fixed credentials**: Set `LOCUST_USERNAME` and `LOCUST_PASSWORD` to log in with an existing account.
- **Auto-register mode**: If `LOCUST_USERNAME` is not provided, each virtual user creates a unique account via `/register/`, then logs in and uploads images as that user.

### Example Run
```bash
cd performance-testing
locust -f locustfile.py --host http://django:8080
```

Optional environment variables:
- `LOCUST_USERNAME`
- `LOCUST_PASSWORD`