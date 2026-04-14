# Michal Sela – Extraction Statistics Dashboard

Interactive Streamlit dashboard that visualises conversation-extraction statistics from Cosmos DB.

## Sections

| Section | What it shows |
|---|---|
| **Overview** | Total conversations, success/error counts, avg messages |
| **Conversations Over Time** | Daily bar chart of extractions |
| **Channel Distribution** | WhatsApp vs Bot Framework pie chart + avg messages per channel |
| **Demographics** | Caller gender pie chart, age distribution histogram |
| **Inquiry Analysis** | Top inquiry subjects, relationship to threat |
| **Referral Analysis** | Where callers were referred, whether they contacted the referral |
| **Outcome Metrics** | Good response rate, wants human callback rate |
| **Raw Data** | Expandable table of all extraction records |

## Prerequisites

- Python 3.10+
- A `.env` file in the project root with Cosmos DB settings:
  ```
  COSMOSDB_CONNECTIONS_STRING=AccountEndpoint=...
  COSMOSDB_EXT_DATABASE=your_ext_db
  COSMOSDB_EXT_CONTAINER=your_ext_container
  COSMOSDB_CONV_DATABASE=your_conv_db
  COSMOSDB_CONV_CONTAINER=your_conv_container
  ```

## Quick Start

```bash
# Install dependencies
pip install -r dashboard/requirements.txt

# Run the dashboard (from project root)
streamlit run dashboard/app.py
```

The dashboard opens at **http://localhost:8501** by default.

## Sidebar Filters

- **Date range** – filter extractions by timestamp
- **Channel** – filter by WhatsApp / Bot Framework
- **Refresh** – clears the 5-minute cache and reloads from Cosmos DB

## Deployment

You can deploy this as a standalone Azure App Service or Azure Container App.  
Streamlit's default port is `8501`; set the startup command to:

```
streamlit run dashboard/app.py --server.port 8000 --server.address 0.0.0.0
```

Alternatively, add it to the existing App Service as a secondary process using a custom startup script.
