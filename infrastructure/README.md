# TODO API Infrastructure

This directory contains Terraform configuration and deployment scripts for deploying the TODO API on AWS ECS Fargate with comprehensive security controls.

## Architecture Overview

The infrastructure includes:

- **VPC**: Custom VPC with public and private subnets across 2 AZs
- **ECS Fargate**: Containerized application deployment
- **Application Load Balancer**: HTTPS-enabled load balancer with SSL termination
- **AWS WAF**: Web Application Firewall for security
- **Auto Scaling**: CPU, memory, and request-based scaling
- **CloudWatch**: Comprehensive monitoring and alerting
- **ECR**: Container registry for Docker images
- **Security Groups**: Restrictive network access controls
- **KMS**: Encryption for logs and SNS topics

## Security Features

### IP Allowlist
- Configurable IP allowlist from `.env` file
- Supports individual IPs and CIDR ranges
- Automatically converts individual IPs to /32 CIDR notation
- If no IP_ALLOWLIST is configured, defaults to open access (0.0.0.0/0)

### AWS WAF Protection
- Rate limiting (2000 requests per 5 minutes per IP)
- AWS Managed Rules for common attacks
- Protection against known bad inputs
- CloudWatch metrics and logging

### Encryption
- ECS logs encrypted with KMS
- SNS topics encrypted with KMS
- S3 ALB logs encrypted
- ECR repository encryption

### Network Security
- Private subnets for ECS tasks
- Public subnets only for load balancer
- Security groups with minimal required access
- NAT gateways for outbound internet access

## Directory Structure

```
infrastructure/
├── terraform/
│   ├── main.tf              # Main Terraform configuration
│   ├── variables.tf         # Input variables
│   ├── outputs.tf           # Output values
│   ├── vpc.tf              # VPC and networking
│   ├── security.tf         # Security groups and WAF
│   ├── load_balancer.tf    # ALB configuration
│   ├── ecs.tf              # ECS cluster and service
│   ├── iam.tf              # IAM roles and policies
│   ├── autoscaling.tf      # Auto scaling configuration
│   └── monitoring.tf       # CloudWatch and SNS
├── scripts/
│   ├── setup.sh            # Environment setup script
│   ├── deploy.sh           # Deployment script
│   └── monitor.sh          # Monitoring and troubleshooting
└── README.md               # This file
```

## Prerequisites

1. **AWS CLI** - Configured with appropriate credentials
2. **Docker** - For building container images
3. **Terraform** - Version 1.0 or later
4. **jq** - For JSON processing in scripts

## Quick Start

### 1. Setup Environment

Run the setup script to install prerequisites and configure AWS:

```bash
cd infrastructure/scripts
./setup.sh
```

### 2. Configure Environment Variables

Review and update the `.env` file in the project root:

```bash
# Example .env configuration
IP_ALLOWLIST=203.0.113.0/24,198.51.100.42/32
DEBUG=false
APP_NAME=TODO API
VERSION=1.0.0
```

### 3. Deploy Infrastructure

Deploy the complete infrastructure:

```bash
./deploy.sh
```

Or run individual steps:

```bash
# Plan deployment
./deploy.sh plan

# Apply infrastructure only
./deploy.sh apply

# Build and push image only
./deploy.sh build

# Deploy application only
./deploy.sh deploy
```

## Configuration Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `aws_region` | AWS region for deployment | `us-east-1` |
| `project_name` | Project name prefix | `todo-api` |
| `environment` | Environment name | `prod` |
| `ip_allowlist` | Comma-separated IP/CIDR list | `""` (open) |
| `container_port` | Application container port | `8000` |
| `cpu` | ECS task CPU units | `512` |
| `memory` | ECS task memory (MB) | `1024` |
| `desired_count` | Initial number of tasks | `2` |
| `min_capacity` | Minimum tasks for auto scaling | `1` |
| `max_capacity` | Maximum tasks for auto scaling | `10` |
| `enable_waf` | Enable AWS WAF | `true` |

## Monitoring and Troubleshooting

Use the monitoring script for operational tasks:

```bash
cd infrastructure/scripts

# Check overall status
./monitor.sh status

# View recent logs
./monitor.sh logs

# View error logs
./monitor.sh errors

# Test application endpoints
./monitor.sh test

# View CloudWatch metrics
./monitor.sh metrics

# Restart the service
./monitor.sh restart

# Scale the service
./monitor.sh scale 5

# Check health status
./monitor.sh health
```

## Accessing the Application

After deployment, the application will be available at:

- **HTTPS**: `https://<alb-dns-name>`
- **Health Check**: `https://<alb-dns-name>/health`
- **API Documentation**: `https://<alb-dns-name>/docs`
- **CloudWatch Dashboard**: Available in AWS Console

## Auto Scaling

The service automatically scales based on:

1. **CPU Utilization**: Target 70%
2. **Memory Utilization**: Target 80%
3. **Request Count**: Target 1000 requests per target

Scaling policies:
- Scale out cooldown: 5 minutes
- Scale in cooldown: 5 minutes
- Min capacity: 1 task
- Max capacity: 10 tasks

## Monitoring and Alerts

### CloudWatch Alarms

- High CPU utilization (>80%)
- High memory utilization (>85%)
- High response time (>1 second)
- High 5XX error rate (>10 errors in 5 minutes)

### Metrics Dashboard

The deployment creates a CloudWatch dashboard with:
- ECS service metrics (CPU, memory)
- ALB metrics (requests, response time, errors)
- Custom application metrics

### Log Groups

- `/ecs/todo-api-prod`: Application logs
- `/ecs/todo-api-prod/exec`: ECS Exec session logs

## Security Considerations

### Network Security
- ECS tasks run in private subnets
- Load balancer in public subnets only
- Security groups restrict access to necessary ports only
- IP allowlist controls external access

### Data Protection
- All logs encrypted with KMS
- SNS topics encrypted
- ECR images scanned for vulnerabilities
- S3 buckets block public access

### Access Control
- IAM roles follow least privilege principle
- ECS tasks have minimal required permissions
- Execution role separate from task role

## Cost Optimization

### Resource Sizing
- Default configuration uses 0.5 vCPU and 1GB memory
- Auto scaling prevents over-provisioning
- ECR lifecycle policies clean up old images

### Monitoring Costs
- CloudWatch log retention set to 30 days
- Metrics and alarms optimized for essential monitoring
- S3 ALB logs for troubleshooting only

## Disaster Recovery

### Backup Strategy
- Container images stored in ECR with lifecycle policies
- Infrastructure as Code in version control
- CloudWatch logs retained for 30 days

### Recovery Procedures
1. Redeploy infrastructure using Terraform
2. ECS service automatically pulls latest image
3. Auto scaling ensures availability across AZs

## Maintenance

### Regular Tasks
1. Review and rotate AWS credentials
2. Update container base images for security patches
3. Review CloudWatch costs and log retention
4. Update Terraform and provider versions

### Updates
1. Update application code
2. Build and push new container image
3. Run `./deploy.sh deploy` to update ECS service

## Troubleshooting

### Common Issues

1. **Service not starting**
   - Check ECS service events
   - Review CloudWatch logs
   - Verify container health checks

2. **High response times**
   - Check CPU/memory utilization
   - Review auto scaling metrics
   - Analyze ALB target health

3. **SSL certificate issues**
   - Verify DNS validation for ACM certificate
   - Check Route 53 records if using custom domain

4. **Access denied errors**
   - Verify IP allowlist configuration
   - Check security group rules
   - Review WAF logs

### Debug Commands

```bash
# Check ECS service status
aws ecs describe-services --cluster todo-api-prod-cluster --services todo-api-prod-service

# View recent ECS events
aws ecs describe-services --cluster todo-api-prod-cluster --services todo-api-prod-service --query 'services[0].events'

# Check ALB target health
aws elbv2 describe-target-health --target-group-arn <target-group-arn>

# View WAF logs
aws logs filter-log-events --log-group-name aws-waf-logs-todo-api-prod
```

## Cleanup

To destroy all infrastructure:

```bash
./deploy.sh destroy
```

**Warning**: This will permanently delete all resources and data.

## Support

For issues or questions:
1. Check the monitoring dashboard
2. Review CloudWatch logs
3. Use the troubleshooting commands above
4. Consult AWS documentation for specific services
