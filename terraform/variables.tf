variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used as prefix for all resources"
  type        = string
  default     = "rag-poc"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "poc"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "Public subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "Private subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.11.0/24", "10.0.12.0/24"]
}

variable "app_port" {
  description = "Application port"
  type        = number
  default     = 8000
}

variable "app_image_tag" {
  description = "Docker image tag to deploy"
  type        = string
  default     = "latest"
}

# ECS sizing
variable "task_cpu" {
  description = "ECS task CPU units (1024 = 1 vCPU)"
  type        = number
  default     = 512
}

variable "task_memory" {
  description = "ECS task memory in MiB"
  type        = number
  default     = 1024
}

variable "desired_count" {
  description = "Initial number of ECS tasks"
  type        = number
  default     = 2
}

variable "min_count" {
  description = "Minimum ECS tasks for auto scaling"
  type        = number
  default     = 1
}

variable "max_count" {
  description = "Maximum ECS tasks for auto scaling"
  type        = number
  default     = 10
}

# Secrets (injected via CI/CD environment variables)
variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "llm_model" {
  description = "OpenAI model to use"
  type        = string
  default     = "gpt-3.5-turbo"
}
