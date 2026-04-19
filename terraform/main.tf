resource "kubernetes_persistent_volume_claim_v1" "postgres_pvc" {
  metadata {
    name      = "postgres-pvc"
    namespace = var.namespace
  }
  spec {
    access_modes = ["ReadWriteMany"]
    resources {
      requests = {
        storage = "1Gi"
      }
    }
  }
}

resource "kubernetes_persistent_volume_claim_v1" "media_pvc" {
  metadata {
    name      = "media-pvc"
    namespace = var.namespace
  }
  spec {
    access_modes = ["ReadWriteMany"]
    resources {
      requests = {
        storage = "1Gi"
      }
    }
  }
}

resource "kubernetes_service_v1" "postgres_svc" {
  metadata {
    name      = "postgres"
    namespace = var.namespace
  }
  spec {
    selector = { app = "postgres" }
    port {
      port        = 5432
      target_port = 5432
    }
  }
}

resource "kubernetes_service_v1" "django_svc" {
  metadata {
    name      = "django"
    namespace = var.namespace
  }
  spec {
    selector = { app = "django" }
    port {
      name        = "http"
      port        = 80
      target_port = 8080
    }
  }
}

resource "kubernetes_deployment_v1" "postgres" {
  metadata {
    name      = "postgres"
    namespace = var.namespace
  }
  spec {
    replicas = 1
    selector {
      match_labels = { app = "postgres" }
    }
    template {
      metadata {
        labels = { app = "postgres" }
      }
      spec {
        container {
          name  = "postgres"
          image = "postgres:18"
          env {
            name  = "POSTGRES_USER"
            value = "admin"
          }
          env {
            name  = "POSTGRES_PASSWORD"
            value = var.db_password
          }
          env {
            name  = "POSTGRES_DB"
            value = "photo_db"
          }
          volume_mount {
            name       = "pgdata"
            mount_path = "/var/lib/postgresql"
          }
        }
        volume {
          name = "pgdata"
          persistent_volume_claim {
            claim_name = kubernetes_persistent_volume_claim_v1.postgres_pvc.metadata[0].name
          }
        }
      }
    }
  }
}

resource "kubernetes_deployment_v1" "django" {
  wait_for_rollout = false
  metadata {
    name      = "django"
    namespace = var.namespace
  }
  spec {
    replicas = 1
    selector {
      match_labels = { app = "django" }
    }
    template {
      metadata {
        labels = { app = "django" }
      }
      spec {
        container {
          name              = "django"
          image             = var.django_image
          image_pull_policy = "Always"
          env {
            name  = "DATABASE_URL"
            value = "postgres://admin:${var.db_password}@postgres:5432/photo_db"
          }
          env {
            name  = "ALLOWED_HOSTS"
            value = "django,django-photo-album.apps.okd.fured.cloud.bme.hu"
          }
          env {
            name  = "CSRF_TRUSTED_ORIGINS"
            value = "https://django-photo-album.apps.okd.fured.cloud.bme.hu"
          }
          volume_mount {
            name       = "media"
            mount_path = "/app/media"
          }
        }
        volume {
          name = "media"
          persistent_volume_claim {
            claim_name = kubernetes_persistent_volume_claim_v1.media_pvc.metadata[0].name
          }
        }
      }
    }
  }
}

