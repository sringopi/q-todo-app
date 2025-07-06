#!/bin/bash

# Terraform Backend Setup Script
# This script creates S3 bucket and DynamoDB table for remote state

set -e

# Configuration
PROJECT_NAME="todo-api"
ENVIRONMENT="prod"
AWS_REGION="us-east-1"
TERRAFORM_DIR="../terraform"

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

# Generate unique suffix for bucket name
SUFFIX=$(date +%s | tail -c 6)
BUCKET_NAME="${PROJECT_NAME}-${ENVIRONMENT}-terraform-state-${SUFFIX}"
TABLE_NAME="${PROJECT_NAME}-${ENVIRONMENT}-terraform-locks"

# Create S3 bucket for Terraform state
create_state_bucket() {
    print_status "Creating S3 bucket for Terraform state: $BUCKET_NAME"
    
    # Create bucket
    aws s3api create-bucket \
        --bucket "$BUCKET_NAME" \
        --region "$AWS_REGION" \
        --create-bucket-configuration LocationConstraint="$AWS_REGION" 2>/dev/null || {
        # Handle us-east-1 special case (no LocationConstraint needed)
        if [ "$AWS_REGION" = "us-east-1" ]; then
            aws s3api create-bucket \
                --bucket "$BUCKET_NAME" \
                --region "$AWS_REGION"
        else
            print_error "Failed to create S3 bucket"
            exit 1
        fi
    }
    
    # Enable versioning
    aws s3api put-bucket-versioning \
        --bucket "$BUCKET_NAME" \
        --versioning-configuration Status=Enabled
    
    # Enable encryption
    aws s3api put-bucket-encryption \
        --bucket "$BUCKET_NAME" \
        --server-side-encryption-configuration '{
            "Rules": [
                {
                    "ApplyServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "AES256"
                    }
                }
            ]
        }'
    
    # Block public access
    aws s3api put-public-access-block \
        --bucket "$BUCKET_NAME" \
        --public-access-block-configuration \
        BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
    
    print_success "S3 bucket created and configured: $BUCKET_NAME"
}

# Create DynamoDB table for state locking
create_locks_table() {
    print_status "Creating DynamoDB table for state locking: $TABLE_NAME"
    
    aws dynamodb create-table \
        --table-name "$TABLE_NAME" \
        --attribute-definitions AttributeName=LockID,AttributeType=S \
        --key-schema AttributeName=LockID,KeyType=HASH \
        --billing-mode PAY_PER_REQUEST \
        --sse-specification Enabled=true \
        --region "$AWS_REGION"
    
    # Wait for table to be active
    print_status "Waiting for DynamoDB table to be active..."
    aws dynamodb wait table-exists --table-name "$TABLE_NAME" --region "$AWS_REGION"
    
    print_success "DynamoDB table created: $TABLE_NAME"
}

# Configure backend in Terraform
configure_backend() {
    print_status "Configuring Terraform backend..."
    
    cd "$TERRAFORM_DIR"
    
    # Create backend configuration file
    cat > backend-config.hcl << EOF
bucket         = "$BUCKET_NAME"
key            = "todo-api/terraform.tfstate"
region         = "$AWS_REGION"
dynamodb_table = "$TABLE_NAME"
encrypt        = true
EOF
    
    # Update backend.tf to use the configuration
    sed -i 's/# bucket/bucket/' backend.tf
    sed -i 's/# key/key/' backend.tf
    sed -i 's/# region/region/' backend.tf
    sed -i 's/# dynamodb_table/dynamodb_table/' backend.tf
    sed -i 's/# encrypt/encrypt/' backend.tf
    
    print_success "Backend configuration created: backend-config.hcl"
    
    cd - >/dev/null
}

# Initialize Terraform with remote backend
init_terraform_backend() {
    print_status "Initializing Terraform with remote backend..."
    
    cd "$TERRAFORM_DIR"
    
    # Initialize with backend configuration
    terraform init -backend-config=backend-config.hcl
    
    print_success "Terraform initialized with remote backend"
    
    cd - >/dev/null
}

# Migrate existing state (if any)
migrate_state() {
    cd "$TERRAFORM_DIR"
    
    if [ -f "terraform.tfstate" ]; then
        print_warning "Local state file found. Migrating to remote backend..."
        
        # The init command above should have prompted for migration
        # If not, we can force it
        terraform init -backend-config=backend-config.hcl -migrate-state -force-copy
        
        print_success "State migrated to remote backend"
        print_warning "You can now safely delete the local terraform.tfstate file"
    fi
    
    cd - >/dev/null
}

# Display backend information
show_backend_info() {
    print_success "Terraform Backend Setup Complete!"
    echo "=================================="
    echo "S3 Bucket: $BUCKET_NAME"
    echo "DynamoDB Table: $TABLE_NAME"
    echo "Region: $AWS_REGION"
    echo ""
    echo "Backend configuration saved to: terraform/backend-config.hcl"
    echo ""
    echo "Next steps:"
    echo "1. Your Terraform state is now stored remotely"
    echo "2. Multiple team members can safely work on the same infrastructure"
    echo "3. State is automatically locked during operations"
    echo "4. State is encrypted and versioned"
    echo ""
    echo "To use this backend in the future:"
    echo "  terraform init -backend-config=backend-config.hcl"
}

# Main function
main() {
    print_status "Setting up Terraform remote backend..."
    
    # Check if AWS CLI is configured
    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        print_error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    # Check if resources already exist
    if aws s3api head-bucket --bucket "$BUCKET_NAME" 2>/dev/null; then
        print_warning "Bucket $BUCKET_NAME already exists. Using existing bucket."
    else
        create_state_bucket
    fi
    
    if aws dynamodb describe-table --table-name "$TABLE_NAME" --region "$AWS_REGION" 2>/dev/null; then
        print_warning "DynamoDB table $TABLE_NAME already exists. Using existing table."
    else
        create_locks_table
    fi
    
    configure_backend
    init_terraform_backend
    migrate_state
    show_backend_info
}

# Handle script arguments
case "${1:-}" in
    "bucket")
        create_state_bucket
        ;;
    "table")
        create_locks_table
        ;;
    "configure")
        configure_backend
        ;;
    "init")
        init_terraform_backend
        ;;
    "info")
        echo "Bucket: $BUCKET_NAME"
        echo "Table: $TABLE_NAME"
        echo "Region: $AWS_REGION"
        ;;
    *)
        main
        ;;
esac
