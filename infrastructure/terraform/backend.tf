# Remote State Backend Configuration
# This stores Terraform state in S3 with DynamoDB locking

terraform {
  backend "s3" {
    # These values will be provided during terraform init
    # bucket         = "your-terraform-state-bucket"
    # key            = "todo-api/terraform.tfstate"
    # region         = "us-east-1"
    # dynamodb_table = "terraform-state-locks"
    # encrypt        = true
  }
}

# Uncomment and customize the resources below to create the backend infrastructure

# # S3 bucket for storing Terraform state
# resource "aws_s3_bucket" "terraform_state" {
#   bucket        = "${var.project_name}-${var.environment}-terraform-state-${random_string.state_suffix.result}"
#   force_destroy = false
# 
#   tags = merge(local.common_tags, {
#     Name        = "Terraform State Bucket"
#     Description = "Stores Terraform state files"
#   })
# }
# 
# resource "aws_s3_bucket_versioning" "terraform_state" {
#   bucket = aws_s3_bucket.terraform_state.id
#   versioning_configuration {
#     status = "Enabled"
#   }
# }
# 
# resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
#   bucket = aws_s3_bucket.terraform_state.id
# 
#   rule {
#     apply_server_side_encryption_by_default {
#       sse_algorithm = "AES256"
#     }
#   }
# }
# 
# resource "aws_s3_bucket_public_access_block" "terraform_state" {
#   bucket = aws_s3_bucket.terraform_state.id
# 
#   block_public_acls       = true
#   block_public_policy     = true
#   ignore_public_acls      = true
#   restrict_public_buckets = true
# }
# 
# # DynamoDB table for state locking
# resource "aws_dynamodb_table" "terraform_locks" {
#   name           = "${var.project_name}-${var.environment}-terraform-locks"
#   billing_mode   = "PAY_PER_REQUEST"
#   hash_key       = "LockID"
# 
#   attribute {
#     name = "LockID"
#     type = "S"
#   }
# 
#   server_side_encryption {
#     enabled = true
#   }
# 
#   tags = merge(local.common_tags, {
#     Name        = "Terraform State Locks"
#     Description = "Stores Terraform state locks"
#   })
# }
# 
# resource "random_string" "state_suffix" {
#   length  = 8
#   special = false
#   upper   = false
# }
# 
# # Outputs for backend configuration
# output "terraform_state_bucket" {
#   description = "S3 bucket for Terraform state"
#   value       = aws_s3_bucket.terraform_state.id
# }
# 
# output "terraform_locks_table" {
#   description = "DynamoDB table for Terraform locks"
#   value       = aws_dynamodb_table.terraform_locks.name
# }
