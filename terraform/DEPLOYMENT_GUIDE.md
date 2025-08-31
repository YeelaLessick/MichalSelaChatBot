# Deployment Guide

## Quick Start

Your multi-environment Terraform infrastructure is now ready! Follow these steps to deploy:

### 1. Prerequisites

Ensure you have:
- Azure CLI installed
- Terraform installed
- Azure subscription access

### 2. Azure Authentication

```bash
# Login to Azure
az login

# Set the correct subscription
az account set --subscription "acd75acf-314c-435d-b215-b212f1586640"

# Verify the subscription
az account show
```

### 3. Deploy Development Environment

```powershell
# Navigate to terraform directory
cd terraform

# Plan development environment (recommended first)
.\deploy.ps1 -Environment dev -Action plan

# Deploy development environment
.\deploy.ps1 -Environment dev -Action apply
```

### 4. Deploy Production Environment

```powershell
# Plan production environment (recommended first)
.\deploy.ps1 -Environment prod -Action plan

# Deploy production environment
.\deploy.ps1 -Environment prod -Action apply
```

## Issue Resolution

**Problem Fixed**: The original deployment attempted to replace production resources when deploying dev environment.

**Solution Implemented**: 
- Terraform workspaces for environment isolation
- Separate state management for dev and prod
- Updated deployment script with workspace selection

The deployment script now automatically:
1. Selects the appropriate workspace (dev/prod)
2. Creates workspace if it doesn't exist
3. Ensures complete isolation between environments

## What Was Created

### File Structure
```
terraform/
├── main.tf                    # Main infrastructure configuration
├── variables.tf               # Variable definitions
├── provider.tf               # Azure provider configuration
├── deploy.ps1                # PowerShell deployment script
├── README.md                 # Detailed documentation
├── environments/
│   ├── dev.tfvars            # Development environment variables
│   └── prod.tfvars           # Production environment variables
└── michalsela-infrastructure.tf.old  # Your original file (backup)
```

### Environment Configurations

**Development Environment (`environments/dev.tfvars`):**
- Resource Group: `michalselabot-dev-rg`
- Storage Account: `samichalseladev01`
- Bot Name: `michalSelaBot-dev`
- App Service: `michalsela-webapp-dev`
- SKU: F1 (Free tier)
- Repository Branch: `develop`

**Production Environment (`environments/prod.tfvars`):**
- Resource Group: `michalselabot-prod-rg`
- Storage Account: `samichalselaprod01`
- Bot Name: `michalSelaBot`
- App Service: `michalsela-webapp`
- SKU: B1 (Basic tier)
- Repository Branch: `main`

## Key Benefits

1. **Environment Isolation**: Separate resource groups for dev and prod
2. **Cost Optimization**: Free tier for development, Basic tier for production
3. **Easy Deployment**: Simple PowerShell script for deployment
4. **Variable Management**: Clean separation of environment-specific variables
5. **Consistent Naming**: Standardized naming conventions across environments

## Next Steps

1. Authenticate with Azure CLI
2. Deploy development environment first to test
3. Once satisfied, deploy production environment
4. Set up CI/CD pipelines to automate deployments

## Troubleshooting

If you encounter authentication issues:
1. Run `az login` and authenticate
2. Verify subscription with `az account show`
3. Ensure you have appropriate permissions in the subscription

For any issues, refer to the detailed README.md file.
