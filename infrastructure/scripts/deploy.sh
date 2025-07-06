#!/bin/bash

# TODO API Deployment Script
# This script builds the Docker image, pushes it to ECR, and deploys to ECS

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

# Function to print colored output
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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command_exists aws; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install it first."
        exit 1
    fi
    
    if ! command_exists terraform; then
        print_error "Terraform is not installed. Please install it first."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        print_error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    print_success "All prerequisites met"
}

# Load environment variables
load_env() {
    if [ -f "../../.env" ]; then
        print_status "Loading environment variables from .env file..."
        export $(grep -v '^#' ../../.env | xargs)
        print_success "Environment variables loaded"
    else
        print_warning ".env file not found. Using default values."
        export IP_ALLOWLIST=""
    fi
}

# Initialize Terraform
init_terraform() {
    print_status "Initializing Terraform..."
    cd "$TERRAFORM_DIR"
    
    terraform init
    
    print_success "Terraform initialized"
}

# Plan Terraform deployment
plan_terraform() {
    print_status "Planning Terraform deployment..."
    
    terraform plan \
        -var="aws_region=$AWS_REGION" \
        -var="project_name=$PROJECT_NAME" \
        -var="environment=$ENVIRONMENT" \
        -var="ip_allowlist=$IP_ALLOWLIST" \
        -out=tfplan
    
    print_success "Terraform plan created"
}

# Apply Terraform
apply_terraform() {
    print_status "Applying Terraform configuration..."
    
    terraform apply tfplan
    
    print_success "Infrastructure deployed successfully"
}

# Get ECR repository URL
get_ecr_url() {
    ECR_URL=$(terraform output -raw ecr_repository_url)
    print_status "ECR Repository URL: $ECR_URL"
}

# Build and push Docker image
build_and_push_image() {
    print_status "Building and pushing Docker image..."
    
    cd ../../
    
    # Get ECR login token
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_URL
    
    # Build image
    print_status "Building Docker image..."
    docker build -t $PROJECT_NAME:latest .
    
    # Tag image for ECR
    docker tag $PROJECT_NAME:latest $ECR_URL:latest
    docker tag $PROJECT_NAME:latest $ECR_URL:$(date +%Y%m%d-%H%M%S)
    
    # Push image
    print_status "Pushing image to ECR..."
    docker push $ECR_URL:latest
    docker push $ECR_URL:$(date +%Y%m%d-%H%M%S)
    
    print_success "Image pushed to ECR successfully"
    
    cd "$TERRAFORM_DIR"
}

# Update ECS service
update_ecs_service() {
    print_status "Updating ECS service..."
    
    CLUSTER_NAME=$(terraform output -raw ecs_cluster_name)
    SERVICE_NAME=$(terraform output -raw ecs_service_name)
    
    # Force new deployment
    aws ecs update-service \
        --cluster $CLUSTER_NAME \
        --service $SERVICE_NAME \
        --force-new-deployment \
        --region $AWS_REGION
    
    print_success "ECS service update initiated"
}

# Wait for deployment to complete
wait_for_deployment() {
    print_status "Waiting for deployment to complete..."
    
    CLUSTER_NAME=$(terraform output -raw ecs_cluster_name)
    SERVICE_NAME=$(terraform output -raw ecs_service_name)
    
    aws ecs wait services-stable \
        --cluster $CLUSTER_NAME \
        --services $SERVICE_NAME \
        --region $AWS_REGION
    
    print_success "Deployment completed successfully"
}

# Display deployment information
show_deployment_info() {
    print_success "Deployment Information:"
    echo "=========================="
    
    ALB_DNS=$(terraform output -raw load_balancer_dns_name)
    DASHBOARD_URL=$(terraform output -raw dashboard_url)
    IP_ALLOWLIST_OUTPUT=$(terraform output -json ip_allowlist | jq -r '.[]' | tr '\n' ',' | sed 's/,$//')
    
    echo "Application URL: https://$ALB_DNS"
    echo "Health Check: https://$ALB_DNS/health"
    echo "API Docs: https://$ALB_DNS/docs"
    echo "CloudWatch Dashboard: $DASHBOARD_URL"
    echo "Allowed IPs: $IP_ALLOWLIST_OUTPUT"
    echo ""
    echo "Note: SSL certificate validation may take some time."
    echo "You can access the application via HTTP initially: http://$ALB_DNS"
}

# Main deployment function
main() {
    print_status "Starting TODO API deployment..."
    
    check_prerequisites
    load_env
    init_terraform
    plan_terraform
    
    # Ask for confirmation
    echo ""
    read -p "Do you want to proceed with the deployment? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Deployment cancelled"
        exit 0
    fi
    
    apply_terraform
    get_ecr_url
    build_and_push_image
    update_ecs_service
    wait_for_deployment
    show_deployment_info
    
    print_success "TODO API deployed successfully!"
}

# Handle script arguments
case "${1:-}" in
    "plan")
        check_prerequisites
        load_env
        init_terraform
        plan_terraform
        ;;
    "apply")
        check_prerequisites
        load_env
        init_terraform
        apply_terraform
        ;;
    "build")
        check_prerequisites
        load_env
        init_terraform
        get_ecr_url
        build_and_push_image
        ;;
    "deploy")
        check_prerequisites
        load_env
        init_terraform
        get_ecr_url
        build_and_push_image
        update_ecs_service
        wait_for_deployment
        ;;
    "destroy")
        print_warning "This will destroy all infrastructure!"
        read -p "Are you sure? Type 'yes' to confirm: " -r
        if [[ $REPLY == "yes" ]]; then
            cd "$TERRAFORM_DIR"
            terraform destroy \
                -var="aws_region=$AWS_REGION" \
                -var="project_name=$PROJECT_NAME" \
                -var="environment=$ENVIRONMENT" \
                -var="ip_allowlist=$IP_ALLOWLIST"
        else
            print_warning "Destroy cancelled"
        fi
        ;;
    *)
        main
        ;;
esac
