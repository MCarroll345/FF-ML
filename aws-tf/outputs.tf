output "cluster_arn" {
  value = data.aws_eks_cluster.cluster.arn
}

output "cluster_certificate_authority" {
  value = data.aws_eks_cluster.cluster.certificate_authority
}

output "cluster_endpoint" {
  value = data.aws_eks_cluster.cluster.endpoint
}

output "cluster_name" {
  value = data.aws_eks_cluster.cluster.name
}

output "oidc_provider_arn" {
  value = data.aws_iam_openid_connect_provider.eks.arn
}
