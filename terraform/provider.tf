terraform {
  backend "kubernetes" {
    secret_suffix    = "state"
    namespace        = "photo-album"
    load_config_file = false
    host             = "https://api.fured.cloud.bme.hu:6443"
  }
}

provider "kubernetes" {
  host  = var.okd_host
  token = var.okd_token
  insecure = true 
}