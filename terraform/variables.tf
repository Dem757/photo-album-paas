variable "okd_host" {
  description = "Az OKD API címe (pl. https://api.okd.fured.cloud.bme.hu:6443)"
  type        = string
}

variable "okd_token" {
  description = "Az OKD bejelentkezési tokened"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "PostgreSQL jelszó"
  type        = string
  sensitive   = true
}

variable "django_image" {
  description = "A Django alkalmazás image elérhetősége"
  type        = string
}

variable "namespace" {
  description = "OKD namespace/project where resources are deployed"
  type        = string
  default     = "postgres-app"
}