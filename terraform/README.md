# Multi-Environment Terraform Infrastructure

This Terraform configuration supports multiple environments (dev and prod) for the Michal Sela ChatBot infrastructure.

## Structure

```
terraform/
├── main.tf                    # Main infrastructure configuration
├── variables.tf               # Variable definitions
├── provider.tf               # Azure provider configuration
├── deploy.ps1                # PowerShell deployment script
├── environments/
│   ├── dev.tfvars            # Development environment variables
│   └── prod.tfvars           # Production environment variables
└── modules/                  # Terraform modules
    ├── resource_group/
    ├── storage_account/
    ├── azure_bot/
    └── app_service/
```

## Environments

### Production (prod)
- Resource Group: `michalselabot-prod-rg`
- Storage Account: `samichalselaprod01`
- Bot Name: `michalSelaBot`
- App Service: `michalsela-webapp`
- SKU: B1 (Basic)
- Branch: `main`

### Development (dev)
- Resource Group: `michalselabot-dev-rg`
- Storage Account: `samichalseladev01`
- Bot Name: `michalSelaBot-dev`
- App Service: `michalsela-webapp-dev`
- SKU: F1 (Free)
- Branch: `develop`

## Deployment

### Using PowerShell Script (Recommended)

```powershell
# Plan deployment for development environment
.\deploy.ps1 -Environment dev -Action plan

# Deploy to development environment
.\deploy.ps1 -Environment dev -Action apply

# Plan deployment for production environment
.\deploy.ps1 -Environment prod -Action plan

# Deploy to production environment
.\deploy.ps1 -Environment prod -Action apply

# Destroy development environment
.\deploy.ps1 -Environment dev -Action destroy
```

### Manual Deployment

```bash
# Initialize Terraform (first time only)
terraform init

# Plan development deployment
terraform plan -var-file="environments/dev.tfvars"

# Apply development deployment
terraform apply -var-file="environments/dev.tfvars"

# Plan production deployment
terraform plan -var-file="environments/prod.tfvars"

# Apply production deployment
terraform apply -var-file="environments/prod.tfvars"
```

## Prerequisites

1. Azure CLI installed and authenticated
2. Terraform installed (version >= 1.0)
3. Appropriate Azure permissions to create resources
4. Valid Azure subscription

## Environment Variables

Each environment file (`environments/*.tfvars`) contains:

- `location`: Azure region
- `resource_group_name`: Resource group name
- `subscription_id`: Azure subscription ID
- `environment`: Environment identifier
- `storage_account_name`: Storage account name
- `bot_name`: Azure Bot name
- `app_service_plan_name`: App Service Plan name
- `app_service_name`: App Service name
- `sku_name`: SKU for App Service Plan
- `bot_sku`: SKU for Azure Bot
- `repo_url`: GitHub repository URL
- `repo_branch`: Git branch to deploy

## State Management

This configuration uses **Terraform Workspaces** for environment isolation:

- **dev workspace**: Development environment state
- **prod workspace**: Production environment state
- **default workspace**: Empty (not used)

Each workspace maintains separate state files, ensuring complete isolation between environments.

For enterprise use, consider:
1. **Azure Storage Backend**: Store Terraform state in Azure Storage
2. **State Locking**: Implement state locking with Azure Storage

## Notes

- Development environment uses F1 (Free) tier for cost optimization
- Production environment uses B1 (Basic) tier for better performance
- Always On is automatically disabled for F1 tier (not supported)
- Each environment deploys to separate resource groups for isolation
