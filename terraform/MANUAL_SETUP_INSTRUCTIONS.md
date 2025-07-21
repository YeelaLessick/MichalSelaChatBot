# Manual Setup Instructions

This document outlines the manual configuration steps required after deploying the infrastructure with Terraform.

## 🚀 Infrastructure Deployed

The following resources have been successfully deployed via Terraform:
- **Resource Group**: `michalselabot-prod-rg`
- **Storage Account**: `samichalselaprod01`
- **App Service Plan**: `michalsela-asp` (B1 Linux)
- **Web App**: `michalsela-webapp` (Python 3.12)
- **Azure Bot Service**: `michalSelaBot` (F0 SKU)
- **Azure AD Application**: Bot authentication and identity

## 📋 Manual Configuration Steps

### 1. Configure Azure Bot Service

The Azure Bot Service has been deployed and integrated with your web app. Complete the following configuration:

**Set Bot Messaging Endpoint:**
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Bot Services** > **michalSelaBot**
3. In the left menu, click **Configuration**
4. Set the **Messaging endpoint** to: `https://michalsela-webapp.azurewebsites.net/api/messages`
5. Click **Apply**

**Test Web Chat:**
1. In the same Bot Service, click **Test in Web Chat** in the left menu
2. This allows you to test your bot directly in the Azure portal
3. Send a test message to verify the bot responds

**Configure Channels (Optional):**
1. Click **Channels** in the left menu
2. Add channels as needed:
   - **Microsoft Teams**: For Teams integration
   - **Web Chat**: For embedding in websites (already available)
   - **Slack, Facebook Messenger**, etc. as needed

### 2. Configure Source Control (GitHub Integration)

Since the automated source control setup failed, configure it manually through Azure Portal:

**Steps:**
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **App Services** > **michalsela-webapp**
3. In the left menu, click **Deployment Center**
4. Choose **GitHub** as the source
5. Authenticate with your GitHub account if prompted
6. Select your organization and repository
7. Choose the branch you want to deploy from (e.g., `main`)
8. Select **GitHub Actions** as the build provider (recommended)
9. Click **Save**

The portal will automatically create a GitHub Actions workflow file in your repository and configure the deployment pipeline.

### 3. Configure Publishing Credentials Security

The app service has been configured with secure defaults, but you may want to verify:

**Steps:**
1. Go to **App Services** > **michalsela-webapp**
2. Navigate to **Deployment Center** > **FTPS credentials**
3. Ensure **FTP state** is set to **FTPS Only** (should already be configured)
4. Verify **Basic authentication** is disabled for both FTP and SCM

### 4. Application Configuration

**Environment Variables:**
The following app settings are already configured:
- `SCM_DO_BUILD_DURING_DEPLOYMENT=1` (enables automatic builds)
- `ENVIRONMENT=production`

**To add additional settings:**
1. Go to **App Services** > **michalsela-webapp** > **Configuration**
2. Click **New application setting** to add:
   - Database connection strings
   - API keys
   - Other environment-specific variables
3. Click **Save** and **Continue** to restart the app

### 5. Enable Monitoring and Diagnostics

**Application Insights (Recommended):**
1. Go to **App Services** > **michalsela-webapp**
2. Click **Application Insights** in the left menu
3. Click **Turn on Application Insights**
4. Choose to create new or use existing Application Insights resource
5. Configure collection settings as needed
6. Click **Apply**

### 6. Custom Domain and SSL (If Required)

**For custom domain:**
1. Go to **App Services** > **michalsela-webapp** > **Custom domains**
2. Click **Add custom domain**
3. Enter your domain name
4. Follow the domain verification process
5. Add DNS records as instructed
6. Once verified, configure SSL certificate (Azure provides free managed certificates)

### 7. Scale and Performance Configuration

**Scaling (if needed beyond B1):**
1. Go to **App Services** > **michalsela-webapp** > **Scale up (App Service plan)**
2. Choose appropriate tier based on requirements
3. For auto-scaling: go to **Scale out (App Service plan)** and configure rules

### 8. Backup Configuration (Recommended for Production)

1. Go to **App Services** > **michalsela-webapp** > **Backups**
2. Configure backup settings:
   - Choose storage account (can use the deployed `samichalselaprod01`)
   - Set backup schedule (daily/weekly)
   - Configure retention policy
3. Click **Save**

### 9. Security Configuration

**Network Security:**
- The app is configured with public access enabled
- To restrict access: go to **Networking** > **Access restrictions**
- Add IP restrictions or integrate with VNet as needed

**Authentication (if required):**
1. Go to **Authentication/Authorization**
2. Turn on App Service Authentication
3. Configure identity providers (Azure AD, GitHub, etc.) if needed

## 🔍 Verification Steps

### Test Your Deployment

1. **Web App Access:**
   - Visit: `https://michalsela-webapp.azurewebsites.net`
   - Verify the app loads correctly (may show default page until code is deployed)

2. **Source Control:**
   - After configuring GitHub integration, make a test commit
   - Go to **Deployment Center** > **Logs** to verify automatic deployment

3. **Application Logs:**
   - Go to **Monitoring** > **Log stream** to view real-time logs
   - Check **App Service logs** under **Monitoring** for stored logs

### Troubleshooting

**Common Issues:**
- **App not loading**: Check application logs and ensure Python dependencies are correctly specified in `requirements.txt`
- **Build failures**: Verify Python 3.12 compatibility and check GitHub Actions workflow
- **Environment variables**: Double-check configuration settings in **Configuration** tab

**Useful Azure CLI Commands:**
```bash
# Check app status
az webapp show --name michalsela-webapp --resource-group michalselabot-prod-rg

# View logs
az webapp log tail --name michalsela-webapp --resource-group michalselabot-prod-rg

# Restart app
az webapp restart --name michalsela-webapp --resource-group michalselabot-prod-rg
```

## 📞 Support Resources

- [Azure App Service Documentation](https://docs.microsoft.com/en-us/azure/app-service/)
- [Python on Azure App Service](https://docs.microsoft.com/en-us/azure/app-service/quickstart-python)
- [GitHub Actions for Azure](https://docs.microsoft.com/en-us/azure/developer/github/github-actions)

## 🔄 Next Steps

1. Complete the source control configuration (Step 1)
2. Add any required environment variables (Step 3)
3. Deploy your application code through the configured GitHub integration
4. Test thoroughly in the production environment
5. Set up monitoring and alerting (Step 4)
6. Configure backup procedures (Step 7)

---

**Note**: This infrastructure is deployed in the `westeurope` region with production-ready security settings. The Terraform modules are reusable and can be deployed to different environments by changing the variables.
