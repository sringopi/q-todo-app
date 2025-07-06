#!/bin/bash

# TODO API Setup Script
# This script sets up the initial environment and prerequisites

set -e

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install AWS CLI
install_aws_cli() {
    if command_exists aws; then
        print_success "AWS CLI is already installed"
        aws --version
        return
    fi
    
    print_status "Installing AWS CLI..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
        unzip awscliv2.zip
        sudo ./aws/install
        rm -rf aws awscliv2.zip
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
        sudo installer -pkg AWSCLIV2.pkg -target /
        rm AWSCLIV2.pkg
    else
        print_error "Unsupported operating system for automatic AWS CLI installation"
        print_status "Please install AWS CLI manually: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
        exit 1
    fi
    
    print_success "AWS CLI installed successfully"
}

# Install Docker
install_docker() {
    if command_exists docker; then
        print_success "Docker is already installed"
        docker --version
        return
    fi
    
    print_status "Installing Docker..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Install Docker on Linux
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker $USER
        rm get-docker.sh
        
        print_warning "Please log out and log back in for Docker group changes to take effect"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        print_error "Please install Docker Desktop for Mac manually: https://docs.docker.com/desktop/mac/install/"
        exit 1
    else
        print_error "Unsupported operating system for automatic Docker installation"
        exit 1
    fi
    
    print_success "Docker installed successfully"
}

# Install Terraform
install_terraform() {
    if command_exists terraform; then
        print_success "Terraform is already installed"
        terraform version
        return
    fi
    
    print_status "Installing Terraform..."
    
    TERRAFORM_VERSION="1.6.6"
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        wget https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip
        unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip
        sudo mv terraform /usr/local/bin/
        rm terraform_${TERRAFORM_VERSION}_linux_amd64.zip
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        wget https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_darwin_amd64.zip
        unzip terraform_${TERRAFORM_VERSION}_darwin_amd64.zip
        sudo mv terraform /usr/local/bin/
        rm terraform_${TERRAFORM_VERSION}_darwin_amd64.zip
    else
        print_error "Unsupported operating system for automatic Terraform installation"
        exit 1
    fi
    
    print_success "Terraform installed successfully"
}

# Install jq
install_jq() {
    if command_exists jq; then
        print_success "jq is already installed"
        return
    fi
    
    print_status "Installing jq..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get update && sudo apt-get install -y jq
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        if command_exists brew; then
            brew install jq
        else
            print_error "Homebrew not found. Please install jq manually or install Homebrew first"
            exit 1
        fi
    else
        print_error "Unsupported operating system for automatic jq installation"
        exit 1
    fi
    
    print_success "jq installed successfully"
}

# Configure AWS credentials
configure_aws() {
    print_status "Configuring AWS credentials..."
    
    if aws sts get-caller-identity >/dev/null 2>&1; then
        print_success "AWS credentials are already configured"
        aws sts get-caller-identity
        return
    fi
    
    print_status "AWS credentials not found. Please configure them now."
    aws configure
    
    # Verify configuration
    if aws sts get-caller-identity >/dev/null 2>&1; then
        print_success "AWS credentials configured successfully"
    else
        print_error "Failed to configure AWS credentials"
        exit 1
    fi
}

# Create .env file if it doesn't exist
setup_env_file() {
    ENV_FILE="../../.env"
    
    if [ -f "$ENV_FILE" ]; then
        print_success ".env file already exists"
        return
    fi
    
    print_status "Creating .env file..."
    
    cp "../../.env.example" "$ENV_FILE"
    
    print_success ".env file created from template"
    print_warning "Please review and update the .env file with your specific configuration"
}

# Validate environment
validate_environment() {
    print_status "Validating environment..."
    
    # Check AWS credentials
    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        print_error "AWS credentials not properly configured"
        exit 1
    fi
    
    # Check Docker
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running or not accessible"
        print_status "Please start Docker and ensure your user is in the docker group"
        exit 1
    fi
    
    # Check Terraform
    if ! terraform version >/dev/null 2>&1; then
        print_error "Terraform is not properly installed"
        exit 1
    fi
    
    print_success "Environment validation passed"
}

# Main setup function
main() {
    print_status "Setting up TODO API deployment environment..."
    
    install_aws_cli
    install_docker
    install_terraform
    install_jq
    configure_aws
    setup_env_file
    validate_environment
    
    print_success "Setup completed successfully!"
    print_status "Next steps:"
    echo "1. Review and update the .env file if needed"
    echo "2. Run './deploy.sh' to deploy the application"
    echo "3. Or run './deploy.sh plan' to see what will be created"
}

# Handle script arguments
case "${1:-}" in
    "aws")
        install_aws_cli
        configure_aws
        ;;
    "docker")
        install_docker
        ;;
    "terraform")
        install_terraform
        ;;
    "validate")
        validate_environment
        ;;
    *)
        main
        ;;
esac
