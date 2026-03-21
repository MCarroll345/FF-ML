variable "name" {
  description = "The name to use for the EKS node group"
  type        = string
  default     = "FF-ml"
}

variable "cluster_name" {
  description = "The name of the existing EKS cluster"
  type        = string
  default     = "FitFinder"
}

variable "min_size" {
  description = "Minimum number of nodes to have in the EKS cluster"
  type        = number
  default     = 1
}

variable "max_size" {
  description = "Maximum number of nodes to have in the EKS cluster"
  type        = number
  default     = 2
}

variable "desired_size" {
  description = "Desired number of nodes to have in the EKS cluster"
  type        = number
  default     = 2
}

variable "instance_types" {
  description = "The types of EC2 instances to run in the node group"
  type        = list(string)
  default     = ["t3.small"]
}

variable "container_port" {
  description = "The port the Docker image listens on"
  type        = number
  default     = 8002
}
