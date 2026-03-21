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
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.17.0"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.0"
    }
  }
}

# ──────────────────────────────────────────────
# Remote state — pull cluster details from k8s-tf
# ──────────────────────────────────────────────

data "terraform_remote_state" "k8s" {
  backend = "local"
  config = {
    path = "../k8s-tf/terraform.tfstate"
  }
}

# ──────────────────────────────────────────────
# Providers
# ──────────────────────────────────────────────

provider "aws" {
  region = "eu-west-1"
}

provider "kubernetes" {
  host                   = data.terraform_remote_state.k8s.outputs.cluster_endpoint
  cluster_ca_certificate = base64decode(data.terraform_remote_state.k8s.outputs.cluster_ca_certificate)
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args        = ["eks", "get-token", "--cluster-name", data.terraform_remote_state.k8s.outputs.cluster_name]
  }
}

provider "helm" {
  kubernetes {
    host                   = data.terraform_remote_state.k8s.outputs.cluster_endpoint
    cluster_ca_certificate = base64decode(data.terraform_remote_state.k8s.outputs.cluster_ca_certificate)
    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      args        = ["eks", "get-token", "--cluster-name", data.terraform_remote_state.k8s.outputs.cluster_name]
    }
  }
}

# ──────────────────────────────────────────────
# KEDA — TriggerAuthentication + ScaledObject
# Applied via kubectl to avoid plan-time CRD validation
# ──────────────────────────────────────────────

resource "local_file" "keda_manifests" {
  filename = "${path.module}/keda-manifests.yaml"
  content  = <<-EOT
    apiVersion: keda.sh/v1alpha1
    kind: TriggerAuthentication
    metadata:
      name: aws-cloudwatch-auth
      namespace: default
    spec:
      podIdentity:
        provider: aws
        identityOwner: keda
    ---
    apiVersion: keda.sh/v1alpha1
    kind: ScaledObject
    metadata:
      name: ${var.name}app-network-scaler
      namespace: default
    spec:
      scaleTargetRef:
        name: ${var.name}app
      minReplicaCount: 2
      maxReplicaCount: 10
      cooldownPeriod: 120
      triggers:
        - type: aws-cloudwatch
          authenticationRef:
            name: aws-cloudwatch-auth
          metricType: AverageValue
          metadata:
            namespace: AWS/EC2
            expression: "SELECT SUM(NetworkIn) FROM \"AWS/EC2\" WHERE AutoScalingGroupName = 'eks-FF-recom-32ce73f7-1d8c-6681-52f9-a1f5e813e739'"
            metricName: NetworkIn
            metricStatPeriod: "60"
            metricCollectionTime: "120"
            metricStat: Sum
            targetMetricValue: "100000"
            minMetricValue: "0"
            awsRegion: eu-west-1
            identityOwner: keda
  EOT
}

resource "null_resource" "keda_manifests" {
  triggers = {
    manifest_hash = local_file.keda_manifests.content_md5
  }

  provisioner "local-exec" {
    command = "kubectl apply -f ${local_file.keda_manifests.filename}"
  }

  depends_on = [
    local_file.keda_manifests
  ]
}