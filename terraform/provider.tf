terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.0.0"
    }
  }
}

provider "kubernetes" {
  host                   = var.okd_host
  token                  = var.okd_token
  insecure               = true
  config_path            = null
  config_context         = null
  config_context_auth_info = null
  config_context_cluster = null
}