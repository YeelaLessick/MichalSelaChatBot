# WhatsApp Integration Setup Guide 📱💜

This guide will help you connect your Azure Communication Services WhatsApp setup to your Michal Sela chatbot.

## 🏗️ Architecture Overview

The implementation uses a clean, organized structure:

```
WhatsApp Messages → Azure Communication Services → Event Grid → Your App → Chatbot Logic
Bot Framework Messages (Telegram, Web Chat) → Azure Bot Service → Your App → Chatbot Logic
```

## 📁 Files Created

- `communication_client.py` - Handles WhatsApp message sending via Azure Communication Services
- `whatsapp_handler.py` - Processes Event Grid webhooks from Communication Services
- `bot_framework_handler.py` - Handles Bot Framework messages (keeps existing channels working)
- Updated `app.py` - Added WhatsApp webhook endpoint `/api/whatsapp/webhook`
- Updated `requirements.txt` - Added Azure Communication Services dependencies
- Updated `.env` - Added configuration placeholders

## 🔧 Configuration Steps

### Step 1: Get Your Communication Services Connection String

1. Go to your **Azure Communication Services** resource in the Azure portal
2. Navigate to **Settings** → **Keys**
3. Copy the **Connection String**
4. Update your `.env` file:
   ```
   COMMUNICATION_SERVICES_CONNECTION_STRING="your_actual_connection_string_here"
   ```

### Step 2: Get Your WhatsApp Channel Registration ID

1. In your **Azure Communication Services** resource, go to **Advanced Messaging** → **WhatsApp**
2. Look for **Channel Registration ID** or **Channel ID**
3. Update your `.env` file:
   ```
   WHATSAPP_CHANNEL_REGISTRATION_ID="your_actual_channel_id_here"
   ```

### Step 3: Create Event Grid Subscription

This is the critical step that connects WhatsApp messages to your bot:

1. In your **Azure Communication Services** resource, go to **Events**
2. Click **+ Event Subscription**
3. Configure the subscription:
   - **Name**: `whatsapp-messages`
   - **Event Types**: Select `Microsoft.Communication.AdvancedMessageReceived`
   - **Endpoint Type**: `Web Hook`
   - **Endpoint**: `https://your-app-service-name.azurewebsites.net/api/whatsapp/webhook`

### Step 4: Deploy Updated Code

1. Install new dependencies:
   ```bash
   pip install azure-communication-messages azure-messaging-eventgrid
   ```

2. Deploy your updated code to Azure App Service

3. Verify deployment by visiting: `https://your-app-service-name.azurewebsites.net/`
   - You should see: "Welcome to Michal Sela Bot! 🤖💜"

### Step 5: Test the Integration

1. Send a WhatsApp message to your business number
2. Check your App Service logs for:
   - `📱 Received WhatsApp webhook request`
   - `🤖 Processing message through chatbot`
   - `✅ WhatsApp response sent successfully`

## 🔍 Troubleshooting

### No Messages Received?

1. **Check Event Grid Subscription**:
   - Ensure the webhook URL is correct
   - Verify the subscription is active
   - Check if there are any delivery failures

2. **Check Communication Services**:
   - Verify WhatsApp Business Account is connected
   - Check if messages show up in Communication Services metrics

3. **Check App Logs**:
   - Look for webhook validation requests
   - Check for any error messages

### Environment Variables Not Set?

If you see errors about missing environment variables:

1. Verify your `.env` file has the correct values
2. If using Azure App Service, set the environment variables in:
   - **Configuration** → **Application settings**

### Dependencies Issues?

If you get import errors:

1. Make sure you've installed the new packages:
   ```bash
   pip install azure-communication-messages azure-messaging-eventgrid
   ```

2. Update your requirements.txt in your deployment

## 📊 Monitoring

### App Service Logs
- Go to **App Service** → **Monitoring** → **Log stream**
- Look for the emoji indicators: 📱 🤖 ✅ ❌

### Communication Services Metrics
- Go to **Communication Services** → **Monitoring** → **Metrics**
- Check "Messages Sent" and "Messages Received"

### Event Grid Metrics
- Go to **Communication Services** → **Events** → Your subscription
- Check delivery success rate and any failures

## 🔄 Message Flow

1. **WhatsApp user sends message** → Azure Communication Services receives it
2. **Communication Services triggers Event Grid** → Sends webhook to your app
3. **Your app processes webhook** → Extracts message and sender info
4. **Chatbot processes message** → Uses your existing Michal Sela logic
5. **App sends response** → Via Communication Services back to WhatsApp

## 🎯 Key Benefits

- **Clean separation**: WhatsApp and Bot Framework channels are isolated
- **Existing channels keep working**: Telegram, Web Chat unchanged
- **Same chatbot logic**: All channels use your Michal Sela chatbot
- **Easy to debug**: Clear logging and error handling
- **Scalable**: Can easily add more channels

## 📝 Next Steps

1. Update your environment variables with actual values
2. Create the Event Grid subscription
3. Deploy the updated code
4. Test with a WhatsApp message
5. Monitor logs to verify everything is working

## 🆘 Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Review Azure portal logs for errors
3. Verify all configuration values are correct
4. Test each component individually

Your WhatsApp integration is now ready! 🎉
