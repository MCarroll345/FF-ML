terraform {
  required_version = ">= 1.0.0, < 2.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.20.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.38.0"
    }
  }
}

# ──────────────────────────────────────────────
# Remote state + data sources
# ──────────────────────────────────────────────

data "terraform_remote_state" "eks" {
  backend = "local"
  config = {
    path = "../aws-tf/terraform.tfstate"
  }
}

data "aws_eks_cluster" "cluster" {
  name = data.terraform_remote_state.eks.outputs.cluster_name
}

locals {
  oidc_issuer         = data.aws_eks_cluster.cluster.identity[0].oidc[0].issuer
  oidc_issuer_stripped = replace(local.oidc_issuer, "https://", "")
}

data "aws_iam_openid_connect_provider" "eks" {
  url = local.oidc_issuer
}

# ──────────────────────────────────────────────
# Providers
# ──────────────────────────────────────────────

provider "kubernetes" {
  host                   = data.aws_eks_cluster.cluster.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority[0].data)
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args        = ["eks", "get-token", "--cluster-name", data.aws_eks_cluster.cluster.name]
  }
}

# ──────────────────────────────────────────────
# IAM — KEDA CloudWatch permissions via IRSA
# ──────────────────────────────────────────────


# ──────────────────────────────────────────────
# Deployment + service
# ──────────────────────────────────────────────

resource "kubernetes_deployment" "nginx" {
  metadata {
    name = "${var.smallname}app"
    labels = {
      App = "${var.name}-app"
    }
  }

  spec {
    replicas = 2
    selector {
      match_labels = {
        App = "${var.name}-app"
      }
    }
    template {
      metadata {
        labels = {
          App = "${var.name}-app"
        }
      }
      spec {
        container {
          image = var.image
          name  = "${var.smallname}container"

          port {
            container_port = var.container_port
          }

          resources {
            limits = {
              cpu    = "0.5"
              memory = "512Mi"
            }
            requests = {
              cpu    = "250m"
              memory = "50Mi"
            }
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "nginx" {
  metadata {
    name = "${var.smallname}service"
  }
  spec {
    selector = {
      App = kubernetes_deployment.nginx.spec[0].template[0].metadata[0].labels.App
    }
    port {
      port        = 80
      target_port = var.container_port
    }
    type = "LoadBalancer"
  }
}