terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

# Local values
locals {
  name_prefix = "${var.project_name}-${var.environment}"
  
  # Parse IP allowlist from environment variable or use default
  ip_allowlist = var.ip_allowlist != "" ? split(",", var.ip_allowlist) : ["0.0.0.0/0"]
  
  # Convert individual IPs to CIDR notation if needed
  normalized_ip_allowlist = [
    for ip in local.ip_allowlist : 
    can(regex("/", ip)) ? trimspace(ip) : "${trimspace(ip)}/32"
  ]
  
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
    Owner       = "sre-team"
  }
}
