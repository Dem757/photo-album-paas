terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.0.0"
    }
  }
  backend "kubernetes" {
    secret_suffix = "state"
    namespace     = "postgres-app"
  }
}

provider "kubernetes" {
}