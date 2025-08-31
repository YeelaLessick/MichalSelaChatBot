# Terraform Multi-Environment Deployment Script
# Usage: .\deploy.ps1 -Environment dev|prod -Action plan|apply|destroy

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("dev", "prod")]
    [string]$Environment,
    
    [Parameter(Mandatory=$true)]
    [ValidateSet("plan", "apply", "destroy")]
    [string]$Action
)

# Set the working directory to the script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptPath

# Define the variable file path
$varFile = "environments\$Environment.tfvars"

# Check if the variable file exists
if (!(Test-Path $varFile)) {
    Write-Error "Variable file $varFile not found!"
    exit 1
}

# Initialize Terraform if .terraform directory doesn't exist
if (!(Test-Path ".terraform")) {
    Write-Host "Initializing Terraform..." -ForegroundColor Yellow
    terraform init
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Terraform init failed!"
        exit 1
    }
}

# Select the appropriate workspace
Write-Host "Selecting workspace: $Environment" -ForegroundColor Yellow
terraform workspace select $Environment
if ($LASTEXITCODE -ne 0) {
    Write-Host "Workspace $Environment doesn't exist, creating it..." -ForegroundColor Yellow
    terraform workspace new $Environment
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create workspace $Environment!"
        exit 1
    }
}

# Execute the Terraform command
Write-Host "Running terraform $Action for $Environment environment..." -ForegroundColor Green

switch ($Action) {
    "plan" {
        terraform plan -var-file="$varFile"
    }
    "apply" {
        terraform apply -var-file="$varFile" -auto-approve
    }
    "destroy" {
        terraform destroy -var-file="$varFile" -auto-approve
    }
}

if ($LASTEXITCODE -ne 0) {
    Write-Error "Terraform $Action failed!"
    exit 1
} else {
    Write-Host "Terraform $Action completed successfully for $Environment environment!" -ForegroundColor Green
}
