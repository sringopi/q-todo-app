#!/bin/bash

# Terraform Backend Cleanup Script
# This script cleans up failed backend resources

set -e

# Configuration
PROJECT_NAME="todo-api"
ENVIRONMENT="prod"
AWS_REGION="us-east-1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Find and cleanup DynamoDB table
cleanup_dynamodb_table() {
    TABLE_NAME="${PROJECT_NAME}-${ENVIRONMENT}-terraform-locks"
    
    print_status "Checking for DynamoDB table: $TABLE_NAME"
    
    TABLE_STATUS=$(aws dynamodb describe-table --table-name "$TABLE_NAME" --region "$AWS_REGION" --query 'Table.TableStatus' --output text 2>/dev/null || echo "NOT_FOUND")
    
    if [ "$TABLE_STATUS" = "NOT_FOUND" ]; then
        print_success "No DynamoDB table found to cleanup"
        return
    fi
    
    print_warning "Found DynamoDB table in $TABLE_STATUS state"
    
    if [ "$TABLE_STATUS" = "CREATING" ] || [ "$TABLE_STATUS" = "UPDATING" ]; then
        print_status "Waiting for table operation to complete..."
        aws dynamodb wait table-exists --table-name "$TABLE_NAME" --region "$AWS_REGION" 2>/dev/null || {
            print_warning "Table operation failed or timed out"
        }
    fi
    
    # Delete the table
    print_status "Deleting DynamoDB table: $TABLE_NAME"
    aws dynamodb delete-table --table-name "$TABLE_NAME" --region "$AWS_REGION" 2>/dev/null || {
        print_error "Failed to delete table. It may not exist or be in a non-deletable state."
        return
    }
    
    print_status "Waiting for table deletion to complete..."
    aws dynamodb wait table-not-exists --table-name "$TABLE_NAME" --region "$AWS_REGION" 2>/dev/null || {
        print_warning "Table deletion may still be in progress"
    }
    
    print_success "DynamoDB table cleanup completed"
}

# Find and cleanup S3 buckets (optional - be careful with this)
list_backend_buckets() {
    print_status "Listing potential backend S3 buckets..."
    
    aws s3api list-buckets --query "Buckets[?contains(Name, '${PROJECT_NAME}-${ENVIRONMENT}-terraform-state')].Name" --output table
}

cleanup_s3_bucket() {
    local bucket_name=$1
    
    if [ -z "$bucket_name" ]; then
        print_error "Please specify bucket name to cleanup"
        echo "Usage: $0 bucket <bucket-name>"
        return 1
    fi
    
    print_warning "This will delete S3 bucket: $bucket_name"
    read -p "Are you sure? Type 'yes' to confirm: " -r
    if [[ $REPLY != "yes" ]]; then
        print_warning "S3 bucket cleanup cancelled"
        return
    fi
    
    print_status "Emptying S3 bucket: $bucket_name"
    aws s3 rm s3://$bucket_name --recursive 2>/dev/null || {
        print_warning "Could not empty bucket or bucket doesn't exist"
    }
    
    print_status "Deleting S3 bucket: $bucket_name"
    aws s3api delete-bucket --bucket $bucket_name --region "$AWS_REGION" 2>/dev/null || {
        print_error "Failed to delete bucket. It may not exist or not be empty."
        return
    }
    
    print_success "S3 bucket cleanup completed"
}

# Main cleanup function
main() {
    print_status "Starting Terraform backend cleanup..."
    
    # Check if AWS CLI is configured
    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        print_error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    cleanup_dynamodb_table
    
    print_success "Backend cleanup completed!"
    print_status "You can now run './setup-backend.sh' to create a fresh backend"
}

# Handle script arguments
case "${1:-}" in
    "table")
        cleanup_dynamodb_table
        ;;
    "bucket")
        cleanup_s3_bucket "$2"
        ;;
    "list")
        list_backend_buckets
        ;;
    *)
        main
        ;;
esac
