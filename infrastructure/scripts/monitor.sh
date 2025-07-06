#!/bin/bash

# TODO API Monitoring Script
# This script provides monitoring and troubleshooting capabilities

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

# Get Terraform outputs
get_terraform_outputs() {
    cd "$TERRAFORM_DIR"
    
    CLUSTER_NAME=$(terraform output -raw ecs_cluster_name 2>/dev/null || echo "")
    SERVICE_NAME=$(terraform output -raw ecs_service_name 2>/dev/null || echo "")
    ALB_DNS=$(terraform output -raw load_balancer_dns_name 2>/dev/null || echo "")
    LOG_GROUP=$(terraform output -raw cloudwatch_log_group_name 2>/dev/null || echo "")
    
    cd - >/dev/null
}

# Check ECS service status
check_ecs_status() {
    print_status "Checking ECS service status..."
    
    if [ -z "$CLUSTER_NAME" ] || [ -z "$SERVICE_NAME" ]; then
        print_error "Unable to get cluster or service name from Terraform outputs"
        return 1
    fi
    
    # Get service details
    SERVICE_INFO=$(aws ecs describe-services \
        --cluster "$CLUSTER_NAME" \
        --services "$SERVICE_NAME" \
        --region "$AWS_REGION" \
        --query 'services[0]' 2>/dev/null)
    
    if [ "$SERVICE_INFO" == "null" ]; then
        print_error "Service not found"
        return 1
    fi
    
    DESIRED_COUNT=$(echo "$SERVICE_INFO" | jq -r '.desiredCount')
    RUNNING_COUNT=$(echo "$SERVICE_INFO" | jq -r '.runningCount')
    PENDING_COUNT=$(echo "$SERVICE_INFO" | jq -r '.pendingCount')
    SERVICE_STATUS=$(echo "$SERVICE_INFO" | jq -r '.status')
    
    echo "Service Status: $SERVICE_STATUS"
    echo "Desired Tasks: $DESIRED_COUNT"
    echo "Running Tasks: $RUNNING_COUNT"
    echo "Pending Tasks: $PENDING_COUNT"
    
    if [ "$RUNNING_COUNT" -eq "$DESIRED_COUNT" ] && [ "$PENDING_COUNT" -eq 0 ]; then
        print_success "Service is healthy"
    else
        print_warning "Service may have issues"
    fi
}

# Check task health
check_task_health() {
    print_status "Checking task health..."
    
    # Get running tasks
    TASK_ARNS=$(aws ecs list-tasks \
        --cluster "$CLUSTER_NAME" \
        --service-name "$SERVICE_NAME" \
        --desired-status RUNNING \
        --region "$AWS_REGION" \
        --query 'taskArns[]' \
        --output text)
    
    if [ -z "$TASK_ARNS" ]; then
        print_warning "No running tasks found"
        return
    fi
    
    # Get task details
    TASKS_INFO=$(aws ecs describe-tasks \
        --cluster "$CLUSTER_NAME" \
        --tasks $TASK_ARNS \
        --region "$AWS_REGION" \
        --query 'tasks[]')
    
    echo "$TASKS_INFO" | jq -r '.[] | "Task: " + .taskArn + " | Status: " + .lastStatus + " | Health: " + (.containers[0].healthStatus // "UNKNOWN")'
}

# Check ALB target health
check_alb_targets() {
    print_status "Checking ALB target health..."
    
    # Get target group ARN
    TARGET_GROUP_ARN=$(aws elbv2 describe-target-groups \
        --names "${PROJECT_NAME}-${ENVIRONMENT}-tg" \
        --region "$AWS_REGION" \
        --query 'TargetGroups[0].TargetGroupArn' \
        --output text 2>/dev/null)
    
    if [ "$TARGET_GROUP_ARN" == "None" ] || [ -z "$TARGET_GROUP_ARN" ]; then
        print_error "Target group not found"
        return 1
    fi
    
    # Get target health
    TARGET_HEALTH=$(aws elbv2 describe-target-health \
        --target-group-arn "$TARGET_GROUP_ARN" \
        --region "$AWS_REGION" \
        --query 'TargetHealthDescriptions[]')
    
    echo "$TARGET_HEALTH" | jq -r '.[] | "Target: " + .Target.Id + " | Port: " + (.Target.Port | tostring) + " | Health: " + .TargetHealth.State'
}

# Get recent logs
get_logs() {
    local hours=${1:-1}
    print_status "Getting logs from the last $hours hour(s)..."
    
    if [ -z "$LOG_GROUP" ]; then
        print_error "Unable to get log group name from Terraform outputs"
        return 1
    fi
    
    # Calculate start time (hours ago)
    START_TIME=$(date -d "$hours hours ago" +%s)000
    
    aws logs filter-log-events \
        --log-group-name "$LOG_GROUP" \
        --start-time "$START_TIME" \
        --region "$AWS_REGION" \
        --query 'events[].[timestamp,message]' \
        --output table
}

# Get error logs
get_error_logs() {
    local hours=${1:-24}
    print_status "Getting error logs from the last $hours hour(s)..."
    
    if [ -z "$LOG_GROUP" ]; then
        print_error "Unable to get log group name from Terraform outputs"
        return 1
    fi
    
    START_TIME=$(date -d "$hours hours ago" +%s)000
    
    aws logs filter-log-events \
        --log-group-name "$LOG_GROUP" \
        --start-time "$START_TIME" \
        --filter-pattern "ERROR" \
        --region "$AWS_REGION" \
        --query 'events[].[timestamp,message]' \
        --output table
}

# Test application endpoints
test_endpoints() {
    print_status "Testing application endpoints..."
    
    if [ -z "$ALB_DNS" ]; then
        print_error "Unable to get ALB DNS name from Terraform outputs"
        return 1
    fi
    
    BASE_URL="https://$ALB_DNS"
    
    # Test health endpoint
    print_status "Testing health endpoint..."
    if curl -s -f "$BASE_URL/health" >/dev/null; then
        print_success "Health endpoint is responding"
    else
        print_error "Health endpoint is not responding"
        # Try HTTP as fallback
        if curl -s -f "http://$ALB_DNS/health" >/dev/null; then
            print_warning "Health endpoint responding on HTTP only"
        fi
    fi
    
    # Test root endpoint
    print_status "Testing root endpoint..."
    if curl -s -f "$BASE_URL/" >/dev/null; then
        print_success "Root endpoint is responding"
    else
        print_error "Root endpoint is not responding"
    fi
    
    # Test API endpoint
    print_status "Testing API endpoint..."
    if curl -s -f "$BASE_URL/api/v1/todos/" >/dev/null; then
        print_success "API endpoint is responding"
    else
        print_error "API endpoint is not responding"
    fi
}

# Show CloudWatch metrics
show_metrics() {
    print_status "Recent CloudWatch metrics..."
    
    # CPU Utilization
    print_status "CPU Utilization (last hour):"
    aws cloudwatch get-metric-statistics \
        --namespace AWS/ECS \
        --metric-name CPUUtilization \
        --dimensions Name=ServiceName,Value="$SERVICE_NAME" Name=ClusterName,Value="$CLUSTER_NAME" \
        --start-time $(date -d '1 hour ago' --iso-8601) \
        --end-time $(date --iso-8601) \
        --period 300 \
        --statistics Average \
        --region "$AWS_REGION" \
        --query 'Datapoints[].{Time:Timestamp,CPU:Average}' \
        --output table
    
    # Memory Utilization
    print_status "Memory Utilization (last hour):"
    aws cloudwatch get-metric-statistics \
        --namespace AWS/ECS \
        --metric-name MemoryUtilization \
        --dimensions Name=ServiceName,Value="$SERVICE_NAME" Name=ClusterName,Value="$CLUSTER_NAME" \
        --start-time $(date -d '1 hour ago' --iso-8601) \
        --end-time $(date --iso-8601) \
        --period 300 \
        --statistics Average \
        --region "$AWS_REGION" \
        --query 'Datapoints[].{Time:Timestamp,Memory:Average}' \
        --output table
}

# Show deployment status
show_status() {
    print_status "TODO API Deployment Status"
    echo "================================"
    
    get_terraform_outputs
    
    if [ -n "$ALB_DNS" ]; then
        echo "Application URL: https://$ALB_DNS"
        echo "Health Check: https://$ALB_DNS/health"
        echo "API Docs: https://$ALB_DNS/docs"
    fi
    
    echo ""
    check_ecs_status
    echo ""
    check_task_health
    echo ""
    check_alb_targets
}

# Restart service
restart_service() {
    print_warning "Restarting ECS service..."
    
    read -p "Are you sure you want to restart the service? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Restart cancelled"
        return
    fi
    
    aws ecs update-service \
        --cluster "$CLUSTER_NAME" \
        --service "$SERVICE_NAME" \
        --force-new-deployment \
        --region "$AWS_REGION"
    
    print_success "Service restart initiated"
}

# Scale service
scale_service() {
    local desired_count=$1
    
    if [ -z "$desired_count" ]; then
        print_error "Please specify desired task count"
        echo "Usage: $0 scale <count>"
        return 1
    fi
    
    print_status "Scaling service to $desired_count tasks..."
    
    aws ecs update-service \
        --cluster "$CLUSTER_NAME" \
        --service "$SERVICE_NAME" \
        --desired-count "$desired_count" \
        --region "$AWS_REGION"
    
    print_success "Service scaling initiated"
}

# Main function
main() {
    get_terraform_outputs
    
    case "${1:-status}" in
        "status")
            show_status
            ;;
        "logs")
            get_logs "${2:-1}"
            ;;
        "errors")
            get_error_logs "${2:-24}"
            ;;
        "test")
            test_endpoints
            ;;
        "metrics")
            show_metrics
            ;;
        "restart")
            restart_service
            ;;
        "scale")
            scale_service "$2"
            ;;
        "health")
            check_ecs_status
            check_task_health
            check_alb_targets
            ;;
        *)
            echo "Usage: $0 {status|logs|errors|test|metrics|restart|scale|health}"
            echo ""
            echo "Commands:"
            echo "  status   - Show overall deployment status"
            echo "  logs     - Show recent application logs (default: 1 hour)"
            echo "  errors   - Show recent error logs (default: 24 hours)"
            echo "  test     - Test application endpoints"
            echo "  metrics  - Show CloudWatch metrics"
            echo "  restart  - Restart the ECS service"
            echo "  scale    - Scale the service (requires count parameter)"
            echo "  health   - Check service and target health"
            ;;
    esac
}

main "$@"
