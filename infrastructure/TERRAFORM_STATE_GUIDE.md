# Terraform State Management Guide

## 🚨 **Critical: Never Commit State Files**

Terraform state files contain sensitive information and should **NEVER** be committed to version control.

## 📁 **What are Terraform State Files?**

- `terraform.tfstate` - Current state of your infrastructure
- `terraform.tfstate.backup` - Previous state backup
- `.terraform.lock.hcl` - Provider version locks (this CAN be committed)

## 🔒 **Security Concerns**

State files may contain:
- Resource IDs and ARNs
- IP addresses and network configurations
- Potentially sensitive data from resources
- Infrastructure topology information

## 🏗️ **Recommended Approach: Remote State**

### **Option 1: Quick Setup with Script (Recommended)**

```bash
cd infrastructure/scripts
./setup-backend.sh
```

This script will:
1. Create an S3 bucket for state storage
2. Create a DynamoDB table for state locking
3. Configure Terraform to use remote backend
4. Migrate any existing local state

### **Option 2: Manual Setup**

1. **Create S3 Bucket**:
```bash
aws s3api create-bucket --bucket your-terraform-state-bucket --region us-east-1
aws s3api put-bucket-versioning --bucket your-terraform-state-bucket --versioning-configuration Status=Enabled
aws s3api put-bucket-encryption --bucket your-terraform-state-bucket --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
```

2. **Create DynamoDB Table**:
```bash
aws dynamodb create-table \
  --table-name terraform-state-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

3. **Configure Backend**:
Edit `infrastructure/terraform/backend.tf` and uncomment the backend configuration:
```hcl
terraform {
  backend "s3" {
    bucket         = "your-terraform-state-bucket"
    key            = "todo-api/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-state-locks"
    encrypt        = true
  }
}
```

4. **Initialize with Backend**:
```bash
cd infrastructure/terraform
terraform init
```

## 🔄 **State Management Commands**

### **View Current State**
```bash
terraform show
terraform state list
```

### **Import Existing Resources**
```bash
terraform import aws_instance.example i-1234567890abcdef0
```

### **Remove Resources from State**
```bash
terraform state rm aws_instance.example
```

### **Move Resources in State**
```bash
terraform state mv aws_instance.old aws_instance.new
```

### **Refresh State**
```bash
terraform refresh
```

## 🔧 **Troubleshooting State Issues**

### **State Lock Issues**
If you get a state lock error:
```bash
# Force unlock (use with caution)
terraform force-unlock LOCK_ID
```

### **State Drift**
If your infrastructure differs from state:
```bash
# Plan to see differences
terraform plan

# Refresh state from actual infrastructure
terraform refresh

# Apply to fix drift
terraform apply
```

### **Corrupted State**
If state is corrupted:
1. Restore from S3 version history
2. Use `terraform import` to rebuild state
3. Use state backup files

## 👥 **Team Collaboration**

### **With Remote State**
✅ Multiple team members can work safely
✅ State is automatically locked during operations
✅ State is backed up and versioned
✅ No risk of state conflicts

### **Best Practices**
1. Always use remote state for shared projects
2. Never edit state files manually
3. Use `terraform import` for existing resources
4. Regular state backups (automatic with S3 versioning)
5. Monitor state file access and changes

## 🚀 **Deployment Workflow**

### **First Time Setup**
```bash
# 1. Setup remote backend
cd infrastructure/scripts
./setup-backend.sh

# 2. Deploy infrastructure
./deploy.sh
```

### **Subsequent Deployments**
```bash
# Deploy changes
./deploy.sh

# Or individual steps
./deploy.sh plan
./deploy.sh apply
```

## 📊 **State File Locations**

### **Local State (Not Recommended for Production)**
- `infrastructure/terraform/terraform.tfstate`
- `infrastructure/terraform/terraform.tfstate.backup`

### **Remote State (Recommended)**
- S3: `s3://your-bucket/todo-api/terraform.tfstate`
- DynamoDB: Lock information in `terraform-state-locks` table

## 🔍 **Monitoring State**

### **S3 Bucket Monitoring**
- Enable CloudTrail for S3 access logging
- Set up CloudWatch alarms for unauthorized access
- Monitor bucket size and version count

### **DynamoDB Monitoring**
- Monitor lock table for stuck locks
- Set up alarms for high read/write activity
- Regular cleanup of old lock records

## 🆘 **Emergency Procedures**

### **Lost State File**
1. Check S3 version history
2. Restore from backup
3. Use `terraform import` to rebuild critical resources
4. Consider infrastructure recreation if state is unrecoverable

### **State Corruption**
1. Stop all Terraform operations
2. Restore from S3 version history
3. Validate state with `terraform plan`
4. If needed, selectively import resources

### **Team Member Conflicts**
1. Communicate before major changes
2. Use feature branches for infrastructure changes
3. Plan and review before applying
4. Use state locking (automatic with remote backend)

## 📋 **Checklist for Production**

- [ ] Remote state backend configured
- [ ] S3 bucket versioning enabled
- [ ] S3 bucket encryption enabled
- [ ] DynamoDB table for locking created
- [ ] State files excluded from version control
- [ ] Team has access to state backend
- [ ] Backup and recovery procedures documented
- [ ] Monitoring and alerting configured

## 🔗 **Related Files**

- `infrastructure/terraform/backend.tf` - Backend configuration
- `infrastructure/terraform/.gitignore` - Excludes state files
- `infrastructure/scripts/setup-backend.sh` - Automated backend setup
- `infrastructure/scripts/deploy.sh` - Deployment with backend support

Remember: **State management is critical for Terraform operations. Always use remote state for production workloads!**
