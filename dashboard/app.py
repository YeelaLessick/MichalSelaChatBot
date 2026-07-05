"""
Michal Sela ChatBot – Extraction Statistics Dashboard
=====================================================
A Streamlit dashboard that queries the Postgres `extractions` table
and displays interactive statistics about conversation insights.

Run with:
    streamlit run dashboard/app.py
"""

import os
import sys
import time
import threading
import io
import calendar
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, timezone
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
from collections import Counter

# Add parent directory to path so we can import config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import MULTI_VALUE_FIELDS

# ---------------------------------------------------------------------------
# Configuration – supports both Streamlit Cloud (st.secrets) and local (.env)
# ---------------------------------------------------------------------------
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))


def _get_secret(st_key: str, env_key: str, default: str = "") -> str:
    """Resolve config from Streamlit secrets first, then env vars.

    Supported Streamlit secrets layouts:
    1) [postgres] block with short keys (host, user, ...)
    2) top-level env-style keys (POSTGRES_HOST, POSTGRES_USER, ...)
    3) top-level short keys (host, user, ...)
    """
    try:
        postgres_block = st.secrets.get("postgres", {})
        if st_key in postgres_block:
            return str(postgres_block[st_key])

        if env_key in st.secrets:
            return str(st.secrets[env_key])

        if st_key in st.secrets:
            return str(st.secrets[st_key])
    except (KeyError, FileNotFoundError, AttributeError):
        pass

    return os.getenv(env_key, default)


PG_HOST     = _get_secret("host",     "POSTGRES_HOST")
PG_PORT     = _get_secret("port",     "POSTGRES_PORT",   "5432")
PG_DB       = _get_secret("database", "POSTGRES_DB",     "chatbot")
PG_USER     = _get_secret("user",     "POSTGRES_USER")
PG_PASSWORD = _get_secret("password", "POSTGRES_PASSWORD")
PG_SSLMODE  = _get_secret("sslmode",  "POSTGRES_SSLMODE", "require")
USE_AAD     = _get_secret("use_aad",  "POSTGRES_USE_AAD", "").lower() in ("1", "true", "yes")


def _get_azure_secret(key: str, default: str = "") -> str:
    """Resolve Azure auth values from st.secrets or environment variables."""
    try:
        azure_block = st.secrets.get("azure", {})
        if key in azure_block:
            return str(azure_block[key])
        if key in st.secrets:
            return str(st.secrets[key])
    except (KeyError, FileNotFoundError, AttributeError):
        pass
    return os.getenv(key, default)


def _get_cost_secret(key: str, env_key: str, default: str = "") -> str:
    """Resolve cost-export config from [cost] secrets, top-level secrets, then env."""
    try:
        cost_block = st.secrets.get("cost", {})
        lookup_keys = [
            key,
            key.lower(),
            key.upper(),
            env_key,
            env_key.lower(),
            env_key.upper(),
        ]

        for lk in lookup_keys:
            if lk in cost_block:
                return str(cost_block[lk])

        for lk in lookup_keys:
            if lk in st.secrets:
                return str(st.secrets[lk])
    except (KeyError, FileNotFoundError, AttributeError):
        pass

    env_lookup = [env_key, env_key.lower(), env_key.upper()]
    for ek in env_lookup:
        val = os.getenv(ek)
        if val:
            return val

    return os.getenv(env_key, default)

# ---------------------------------------------------------------------------
# Postgres helpers (with AAD token caching)
# ---------------------------------------------------------------------------

_AAD_SCOPE = "https://ossrdbms-aad.database.windows.net/.default"
_token_cache: dict = {"token": None, "expires_at": 0.0}
_token_lock = threading.Lock()


def _get_aad_token() -> str:
    now = time.time()
    with _token_lock:
        cached = _token_cache["token"]
        if cached and _token_cache["expires_at"] - now > 300:
            return cached
        from azure.identity import DefaultAzureCredential

        tenant_id = _get_azure_secret("AZURE_TENANT_ID")
        client_id = _get_azure_secret("AZURE_CLIENT_ID")
        client_secret = _get_azure_secret("AZURE_CLIENT_SECRET")

        # Streamlit Cloud doesn't provide Managed Identity. Prefer explicit
        # service-principal credentials when supplied in secrets.
        if tenant_id and client_id and client_secret:
            from azure.identity import ClientSecretCredential

            cred = ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret,
            )
        else:
            cred = DefaultAzureCredential(
                managed_identity_client_id=client_id or None
            )

        access = cred.get_token(_AAD_SCOPE)
        _token_cache["token"] = access.token
        _token_cache["expires_at"] = float(access.expires_on)
        return access.token


def _connect() -> psycopg.Connection:
    """Open a fresh Postgres connection (AAD or password)."""
    if not PG_HOST or not PG_USER:
        raise RuntimeError(
            "Postgres connection not configured. Set POSTGRES_HOST / POSTGRES_USER "
            "(and POSTGRES_PASSWORD or POSTGRES_USE_AAD=true) in .env or st.secrets."
        )
    password = _get_aad_token() if USE_AAD else PG_PASSWORD
    return psycopg.connect(
        host=PG_HOST,
        port=int(PG_PORT),
        dbname=PG_DB,
        user=PG_USER,
        password=password,
        sslmode=PG_SSLMODE,
        connect_timeout=10,
        row_factory=dict_row,
    )


def _get_azure_credential():
    """Create an Azure credential for Blob access.

    Streamlit Cloud should use service principal credentials from secrets.
    """
    from azure.identity import ClientSecretCredential, DefaultAzureCredential

    tenant_id = _get_azure_secret("AZURE_TENANT_ID")
    client_id = _get_azure_secret("AZURE_CLIENT_ID")
    client_secret = _get_azure_secret("AZURE_CLIENT_SECRET")

    if tenant_id and client_id and client_secret:
        return ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
        )

    return DefaultAzureCredential(managed_identity_client_id=client_id or None)


@st.cache_data(ttl=1800)
def load_cost_export() -> pd.DataFrame:
    """Load Azure Cost Management export CSV files from Blob Storage."""
    account = _get_cost_secret("storage_account", "COST_STORAGE_ACCOUNT")
    container = _get_cost_secret("container", "COST_CONTAINER", "cost-exports")
    directory = _get_cost_secret("directory", "COST_DIRECTORY", "cost/daily")

    if not account:
        return pd.DataFrame()

    try:
        from azure.storage.blob import BlobServiceClient

        account_url = f"https://{account}.blob.core.windows.net"
        blob_service = BlobServiceClient(account_url=account_url, credential=_get_azure_credential())
        container_client = blob_service.get_container_client(container)

        blobs = list(container_client.list_blobs(name_starts_with=directory))
        if not blobs:
            return pd.DataFrame()

        # Load newest files first and cap to avoid heavy dashboard startup.
        blobs = sorted(blobs, key=lambda b: b.last_modified or datetime.min.replace(tzinfo=timezone.utc), reverse=True)[:20]

        frames = []
        for blob in blobs:
            if not blob.name.lower().endswith(".csv"):
                continue
            data = container_client.download_blob(blob.name).readall()
            try:
                df_blob = pd.read_csv(io.BytesIO(data))
                if not df_blob.empty:
                    frames.append(df_blob)
            except Exception:
                # Skip malformed files and continue.
                continue

        if not frames:
            return pd.DataFrame()

        return pd.concat(frames, ignore_index=True)
    except Exception:
        return pd.DataFrame()


def _normalise_cost_dataframe(df_cost: pd.DataFrame) -> pd.DataFrame:
    """Map export schema variants to a common shape: date + cost."""
    if df_cost.empty:
        return df_cost

    date_col = next(
        (c for c in ["Date", "UsageDate", "date", "usageDate"] if c in df_cost.columns),
        None,
    )
    cost_col = next(
        (c for c in ["CostInBillingCurrency", "PreTaxCost", "Cost", "costInBillingCurrency"] if c in df_cost.columns),
        None,
    )

    if not date_col or not cost_col:
        return pd.DataFrame()

    out = pd.DataFrame()

    # Cost export sometimes uses yyyymmdd integers in UsageDate.
    if date_col.lower() == "usagedate":
        out["date"] = pd.to_datetime(df_cost[date_col].astype(str), format="%Y%m%d", errors="coerce", utc=True)
    else:
        out["date"] = pd.to_datetime(df_cost[date_col], errors="coerce", utc=True)

    out["cost"] = pd.to_numeric(df_cost[cost_col], errors="coerce").fillna(0.0)
    out = out.dropna(subset=["date"]) 
    return out


@st.cache_data(ttl=300)  # cache for 5 minutes
def load_extractions() -> pd.DataFrame:
    """Fetch all extraction documents from Postgres and return as a DataFrame."""
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                # Postgres does the JSON projection for us – way more efficient
                # than fetching whole documents and unpacking in Python.
                cur.execute(
                    """
                    SELECT
                        session_id,
                        extraction,
                        metadata,
                        COALESCE(
                            (extraction->>'extraction_timestamp')::timestamptz,
                            (metadata->>'extraction_timestamp')::timestamptz,
                            created_at
                        ) AS extraction_timestamp,
                        COALESCE((extraction->>'message_count')::int, 0) AS message_count,
                        COALESCE(metadata->>'channel', 'unknown')        AS channel,
                        metadata->>'phone_number'                        AS phone_number,
                        (extraction ? 'extraction_error')                AS has_error
                    FROM extractions
                    ORDER BY created_at DESC
                    """
                )
                items = cur.fetchall()

        if not items:
            return pd.DataFrame()

        rows = []
        for item in items:
            extraction = item.get("extraction") or {}
            fields = extraction.get("extracted_fields", {}) if isinstance(extraction, dict) else {}
            rows.append({
                "session_id":           item["session_id"],
                "extraction_timestamp": item["extraction_timestamp"],
                "message_count":        item["message_count"],
                "channel":              item["channel"],
                "phone_number":         item["phone_number"],
                "has_error":            item["has_error"],
                "conversation_time":    fields.get("conversation_time"),
                "inquiry_subject":      fields.get("inquiry_subject"),
                "caller_age":           fields.get("caller_age"),
                "caller_gender":        fields.get("caller_gender"),
                "relationship_to_threat": fields.get("relationship_to_threat"),
                "referred_to":          fields.get("referred_to"),
                "wants_human_callback": fields.get("wants_human_callback"),
                "urgency_level":        fields.get("urgency_level"),
            })

        df = pd.DataFrame(rows)

        # Normalise multi-value fields: ensure they are always lists
        for col in MULTI_VALUE_FIELDS:
            if col in df.columns:
                df[col] = df[col].apply(
                    lambda v: v if isinstance(v, list) else ([v] if v is not None and v == v else [])
                )

        # Parse timestamp
        if "extraction_timestamp" in df.columns:
            df["extraction_timestamp"] = pd.to_datetime(
                df["extraction_timestamp"], errors="coerce", utc=True
            )

        return df

    except Exception as e:
        st.error(f"Error loading data from Postgres: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def load_conversations() -> pd.DataFrame:
    """Fetch conversation metadata (message counts) from Postgres."""
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        session_id,
                        jsonb_array_length(conversation) AS msg_count
                    FROM conversations
                    """
                )
                rows = cur.fetchall()
        if not rows:
            return pd.DataFrame()
        return pd.DataFrame(rows)
    except Exception as e:
        st.error(f"Error loading conversations: {e}")
        return pd.DataFrame()


def _explode_multi(df: pd.DataFrame, col: str) -> pd.Series:
    """Explode a list-valued column and return the individual values (drop empties)."""
    exploded = df[col].explode().dropna()
    exploded = exploded[exploded.astype(str).str.strip() != ""]
    return exploded


# ---------------------------------------------------------------------------
# Helper: normalise yes/no Hebrew values to boolean-like labels
# ---------------------------------------------------------------------------
YES_VALUES = {"כן", "yes", "true", "1", "נכון"}
NO_VALUES = {"לא", "no", "false", "0"}


def normalise_yesno(value) -> str | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    v = str(value).strip().lower()
    if v in YES_VALUES:
        return "כן"
    if v in NO_VALUES:
        return "לא"
    return str(value).strip() or None


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Michal Sela – Extraction Dashboard",
    page_icon="💜",
    layout="wide",
)

st.title("💜 Michal Sela Chatbot – Extraction Statistics")
st.caption("Live statistics from conversation extractions stored in Postgres")

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
with st.spinner("Loading data from Postgres …"):
    df = load_extractions()

if df.empty:
    st.warning(
        "No extraction data found. Make sure the Postgres connection settings "
        "(POSTGRES_HOST / POSTGRES_USER / POSTGRES_PASSWORD or POSTGRES_USE_AAD) "
        "are configured in your `.env` file."
    )
    st.stop()

# Sidebar: filters
st.sidebar.header("🔎 Filters")

# Date range filter
if "extraction_timestamp" in df.columns and df["extraction_timestamp"].notna().any():
    min_date = df["extraction_timestamp"].min().date()
    max_date = df["extraction_timestamp"].max().date()
    date_range = st.sidebar.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if len(date_range) == 2:
        start, end = date_range
        mask = (df["extraction_timestamp"].dt.date >= start) & (
            df["extraction_timestamp"].dt.date <= end
        )
        df = df[mask]

# Channel filter
channels = df["channel"].dropna().unique().tolist()
if channels:
    selected_channels = st.sidebar.multiselect("Channel", channels, default=channels)
    df = df[df["channel"].isin(selected_channels)]

# Phone number search (partial match)
phone_query = st.sidebar.text_input("Phone number", value="").strip()
if phone_query and "phone_number" in df.columns:
    df = df[
        df["phone_number"].fillna("").astype(str).str.contains(phone_query, case=False, regex=False)
    ]

# Refresh button
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info(f"Showing **{len(df)}** extraction records")

# ---------------------------------------------------------------------------
# Cost Overview (from Azure Cost export in Blob Storage)
# ---------------------------------------------------------------------------
st.header("💸 Cost Overview")

cost_raw = load_cost_export()
cost_df = _normalise_cost_dataframe(cost_raw)

if cost_df.empty:
    st.info(
        "Cost export is not configured yet. Add Streamlit secrets under [cost]: "
        "storage_account, container (default cost-exports), directory (default cost/daily), "
        "and optional monthly_budget_usd."
    )
else:
    now_utc = datetime.now(timezone.utc)
    month_start = now_utc.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_mask = (cost_df["date"] >= month_start) & (cost_df["date"] <= now_utc)
    mtd_df = cost_df[month_mask]

    mtd_cost = float(mtd_df["cost"].sum()) if not mtd_df.empty else 0.0
    days_elapsed = max(1, now_utc.day)
    days_in_month = calendar.monthrange(now_utc.year, now_utc.month)[1]
    forecast_eom = (mtd_cost / days_elapsed) * days_in_month

    monthly_budget_raw = _get_cost_secret("monthly_budget_usd", "COST_MONTHLY_BUDGET_USD", "")
    monthly_budget = float(monthly_budget_raw) if monthly_budget_raw else None
    remaining = (monthly_budget - mtd_cost) if monthly_budget is not None else None

    c1, c2, c3 = st.columns(3)
    c1.metric("MTD Cost (USD)", f"${mtd_cost:,.2f}")
    c2.metric("Forecast EOM (USD)", f"${forecast_eom:,.2f}")
    c3.metric("Remaining Budget (USD)", f"${remaining:,.2f}" if remaining is not None else "-")

    daily = (
        mtd_df.assign(day=mtd_df["date"].dt.date)
        .groupby("day", as_index=False)["cost"]
        .sum()
    )
    fig_cost = px.line(
        daily,
        x="day",
        y="cost",
        markers=True,
        title="Daily Cost Trend (MTD)",
        labels={"day": "Date", "cost": "Cost (USD)"},
    )
    st.plotly_chart(fig_cost, width="stretch")

# ---------------------------------------------------------------------------
# KPIs – top row
# ---------------------------------------------------------------------------
st.header("📊 Overview")

total = len(df)
success = df[~df["has_error"]].shape[0]
errors = df[df["has_error"]].shape[0]
avg_messages = df["message_count"].mean() if total > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Conversations", total)
col2.metric("Successful Extractions", success)
col3.metric("Extraction Errors", errors)
col4.metric("Avg Messages / Conv", f"{avg_messages:.1f}")

# Unique callers (by phone) and returning callers
if "phone_number" in df.columns:
    phones = df["phone_number"].dropna()
    unique_callers = phones.nunique()
    returning_callers = (phones.value_counts() > 1).sum()
else:
    unique_callers = "-"
    returning_callers = "-"

avg_duration = df["conversation_time"].dropna().mean() if "conversation_time" in df.columns else 0

col5, col6, col7 = st.columns(3)
col5.metric("Unique Callers (phone)", unique_callers)
col6.metric("Returning Callers", returning_callers)
col7.metric("Avg Duration (min)", f"{avg_duration:.1f}" if avg_duration else "-")

# ---------------------------------------------------------------------------
# Conversations over time
# ---------------------------------------------------------------------------
if "extraction_timestamp" in df.columns and df["extraction_timestamp"].notna().any():
    st.subheader("📅 Conversations Over Time")
    df_time = df.set_index("extraction_timestamp").resample("D").size().reset_index(name="count")
    fig_time = px.bar(
        df_time,
        x="extraction_timestamp",
        y="count",
        labels={"extraction_timestamp": "Date", "count": "Conversations"},
        color_discrete_sequence=["#9b59b6"],
    )
    fig_time.update_layout(bargap=0.2)
    st.plotly_chart(fig_time, width="stretch")

# ---------------------------------------------------------------------------
# Channel distribution
# ---------------------------------------------------------------------------
st.subheader("📡 Channel Distribution")
col_ch1, col_ch2 = st.columns(2)

channel_counts = df["channel"].value_counts().reset_index()
channel_counts.columns = ["channel", "count"]
fig_channel = px.pie(
    channel_counts,
    values="count",
    names="channel",
    color_discrete_sequence=px.colors.qualitative.Set2,
)
col_ch1.plotly_chart(fig_channel, width="stretch")

# Channel vs average message count
channel_msg = df.groupby("channel")["message_count"].mean().reset_index()
channel_msg.columns = ["channel", "avg_messages"]
fig_ch_msg = px.bar(
    channel_msg,
    x="channel",
    y="avg_messages",
    labels={"channel": "Channel", "avg_messages": "Avg Messages"},
    color_discrete_sequence=["#2ecc71"],
)
col_ch2.plotly_chart(fig_ch_msg, width="stretch")

# ---------------------------------------------------------------------------
# Demographics
# ---------------------------------------------------------------------------
st.header("👤 Demographics")
col_d1, col_d2 = st.columns(2)

# Gender
gender_counts = df["caller_gender"].dropna().value_counts().reset_index()
gender_counts.columns = ["gender", "count"]
if not gender_counts.empty:
    fig_gender = px.pie(
        gender_counts,
        values="count",
        names="gender",
        title="Caller Gender (מין הפונה)",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    col_d1.plotly_chart(fig_gender, width="stretch")
else:
    col_d1.info("No gender data available")

# Age – now always categorical (age ranges from extraction)
AGE_RANGE_ORDER = ["מתחת ל-18", "18-25", "26-35", "36-45", "46-55", "56-65", "מעל 65", "לא ידוע"]
age_values = df["caller_age"].dropna()
if not age_values.empty:
    age_cat = age_values.value_counts().reset_index()
    age_cat.columns = ["age_range", "count"]
    # Sort by predefined order
    age_cat["sort_key"] = age_cat["age_range"].apply(
        lambda x: AGE_RANGE_ORDER.index(x) if x in AGE_RANGE_ORDER else 99
    )
    age_cat = age_cat.sort_values("sort_key").drop(columns="sort_key")
    fig_age = px.bar(
        age_cat,
        x="age_range",
        y="count",
        title="Caller Age Distribution (גיל הפונה)",
        labels={"age_range": "Age Range", "count": "Count"},
        color_discrete_sequence=["#3498db"],
    )
    col_d2.plotly_chart(fig_age, width="stretch")
else:
    col_d2.info("No age data available")

# ---------------------------------------------------------------------------
# Inquiry Analysis
# ---------------------------------------------------------------------------
st.header("📋 Inquiry Analysis")
col_i1, col_i2 = st.columns(2)

# Inquiry subject
subject_values = _explode_multi(df, "inquiry_subject")
subject_counts = subject_values.value_counts().reset_index()
subject_counts.columns = ["subject", "count"]
if not subject_counts.empty:
    fig_subject = px.bar(
        subject_counts.head(15),
        x="count",
        y="subject",
        orientation="h",
        title="Top Inquiry Subjects (נושא הפניה)",
        labels={"subject": "Subject", "count": "Count"},
        color_discrete_sequence=["#e74c3c"],
    )
    fig_subject.update_layout(yaxis=dict(autorange="reversed"))
    col_i1.plotly_chart(fig_subject, width="stretch")
else:
    col_i1.info("No inquiry subject data available")

# Relationship to threat
rel_counts = df["relationship_to_threat"].dropna().value_counts().reset_index()
rel_counts.columns = ["relationship", "count"]
if not rel_counts.empty:
    fig_rel = px.bar(
        rel_counts.head(10),
        x="count",
        y="relationship",
        orientation="h",
        title="Relationship to Threat (קרבה לגורם המאיים)",
        labels={"relationship": "Relationship", "count": "Count"},
        color_discrete_sequence=["#f39c12"],
    )
    fig_rel.update_layout(yaxis=dict(autorange="reversed"))
    col_i2.plotly_chart(fig_rel, width="stretch")
else:
    col_i2.info("No relationship data available")

# ---------------------------------------------------------------------------
# Referrals
# ---------------------------------------------------------------------------
st.header("🔗 Referral Analysis")

# Where referred
referred_values = _explode_multi(df, "referred_to")
referred_counts = referred_values.value_counts().reset_index()
referred_counts.columns = ["referred_to", "count"]
if not referred_counts.empty:
    fig_referred = px.bar(
        referred_counts.head(15),
        x="count",
        y="referred_to",
        orientation="h",
        title="Where We Referred (לאן הפנינו)",
        labels={"referred_to": "Referral Destination", "count": "Count"},
        color_discrete_sequence=["#1abc9c"],
    )
    fig_referred.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_referred, width="stretch")
else:
    st.info("No referral data available")

# ---------------------------------------------------------------------------
# Outcome Metrics
# ---------------------------------------------------------------------------
st.header("✅ Outcome Metrics")
col_o1 = st.columns(1)[0]

# Wants human callback
df["callback_norm"] = df["wants_human_callback"].apply(normalise_yesno)
callback_counts = df["callback_norm"].dropna().value_counts().reset_index()
callback_counts.columns = ["callback", "count"]
if not callback_counts.empty:
    fig_callback = px.pie(
        callback_counts,
        values="count",
        names="callback",
        title="Wants Human Callback? (האם רוצה שנציג יחזור)",
        color_discrete_sequence=["#3498db", "#e67e22", "#95a5a6"],
    )
    col_o1.plotly_chart(fig_callback, width="stretch")
else:
    col_o1.info("No callback data available")

# ---------------------------------------------------------------------------
# Urgency & Conversation Duration
# ---------------------------------------------------------------------------
st.header("⚠️ Urgency & Duration")
col_u1, col_u2 = st.columns(2)

# Urgency level
if "urgency_level" in df.columns:
    urgency_counts = df["urgency_level"].dropna().value_counts().reset_index()
    urgency_counts.columns = ["urgency", "count"]
    if not urgency_counts.empty:
        URGENCY_ORDER = ["חירום - סכנת חיים מיידית", "גבוהה - מצב מסוכן", "בינונית - דורש טיפול", "נמוכה - בקשת מידע בלבד"]
        urgency_counts["sort_key"] = urgency_counts["urgency"].apply(
            lambda x: URGENCY_ORDER.index(x) if x in URGENCY_ORDER else 99
        )
        urgency_counts = urgency_counts.sort_values("sort_key").drop(columns="sort_key")
        fig_urgency = px.bar(
            urgency_counts,
            x="count",
            y="urgency",
            orientation="h",
            title="Urgency Level (רמת דחיפות)",
            labels={"urgency": "Urgency", "count": "Count"},
            color="urgency",
            color_discrete_map={
                "חירום - סכנת חיים מיידית": "#e74c3c",
                "גבוהה - מצב מסוכן": "#e67e22",
                "בינונית - דורש טיפול": "#f1c40f",
                "נמוכה - בקשת מידע בלבד": "#2ecc71",
            },
        )
        fig_urgency.update_layout(yaxis=dict(autorange="reversed"), showlegend=False)
        col_u1.plotly_chart(fig_urgency, width="stretch")
    else:
        col_u1.info("No urgency data available")
else:
    col_u1.info("No urgency data available")

# Conversation duration distribution
if "conversation_time" in df.columns:
    duration_vals = df["conversation_time"].dropna()
    if not duration_vals.empty:
        fig_dur = px.histogram(
            duration_vals,
            nbins=20,
            title="Conversation Duration Distribution (minutes)",
            labels={"value": "Duration (min)", "count": "Count"},
            color_discrete_sequence=["#9b59b6"],
        )
        col_u2.plotly_chart(fig_dur, width="stretch")
    else:
        col_u2.info("No duration data available")
else:
    col_u2.info("No duration data available")

# ---------------------------------------------------------------------------
# Raw Data Table
# ---------------------------------------------------------------------------
st.header("📄 Raw Extraction Data")
with st.expander("Show raw data table", expanded=False):
    display_cols = [
        "session_id",
        "extraction_timestamp",
        "channel",
        "phone_number",
        "message_count",
        "conversation_time",
        "urgency_level",
        "inquiry_subject",
        "caller_age",
        "caller_gender",
        "relationship_to_threat",
        "referred_to",
        "wants_human_callback",
        "has_error",
    ]
    available_cols = [c for c in display_cols if c in df.columns]
    display_df = df[available_cols].copy()
    # Join array fields into readable comma-separated strings for display
    for col in MULTI_VALUE_FIELDS:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(
                lambda v: ", ".join(v) if isinstance(v, list) else v
            )
    st.dataframe(
        display_df.sort_values("extraction_timestamp", ascending=False),
        width="stretch",
        hide_index=True,
    )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("---")
st.caption(
    f"Dashboard last refreshed: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} · "
    f"Data source: Postgres ({PG_DB}@{PG_HOST})"
)
