output "lb_ip" {
  value = try(kubernetes_service.nginx.status[0].load_balancer[0].ingress[0].hostname, "not yet assigned")
}

output "cluster_endpoint" {
  value = data.aws_eks_cluster.cluster.endpoint
}

output "cluster_ca_certificate" {
  value = data.aws_eks_cluster.cluster.certificate_authority[0].data
}

output "cluster_name" {
  value = data.aws_eks_cluster.cluster.name
}

