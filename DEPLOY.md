# Deployment Guide: Martian Investment System

This guide covers how to deploy the modern **Martian Architecture** (Next.js Frontend + FastAPI Backend).

## 🏗️ Architecture Overview

The system is now split into two services:
1.  **Backend (Python/FastAPI)**: Handles API logic, Database, and AI. Runs on Port 8000.
2.  **Frontend (Next.js)**: Handles the UI, Auth redirects, and Proxies API calls. Runs on Port 3000.

**You need to deploy TWO services.**

> [!CAUTION]
> **CRITICAL DATA WARNING**: The Backend Service contains the persistent database in `/data`.
> **DO NOT DELETE** the Backend Service to redeploy. Use the **"Redeploy"** button instead.
> Deleting the service will **DELETE THE DATABASE** permanently!

---

## ⚡ Recommended: Zeabur (Best Performance)

[Zeabur](https://zeabur.com) handles multi-service deployments (like this one) effortlessly.

### Step 1: Deploy Backend (Python)
1.  Create a Project in Zeabur.
2.  **Add Service** -> **Git** -> Select `martian` repo.
3.  **Config**:
    - Right-click the service used for Backend.
    - **Service Name**: `martian-backend`
    - **Root Directory**: `.` (Current root)
    - **Build Command**: `uv pip compile pyproject.toml -o requirements.txt` (or ensure requirements.txt is present)
    - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
4.  **Networking**:
    - **Port**: 8000
    - **Domain**: Generate one (e.g., `martian-api.zeabur.app`). **Copy this URL.**

### Step 2: Deploy Frontend (Next.js)
1.  In the *same* Zeabur Project, **Add Service** -> **Git** -> Select `martian` repo (again).
2.  **Config**:
    - Right-click this new service.
    - **Service Name**: `martian-frontend`
    - **Root Directory**: `frontend` (Important!)
    - **Framework**: Next.js (Auto-detected)
3.  **Networking**:
    - **Port**: 3000
    - **Domain**: Generate one (e.g., `martian-app.zeabur.app`). **This is your App URL.**
4.  **Enviroment Variables** (In Frontend Service):
    - `NEXT_PUBLIC_API_URL`: `https://martian-api.zeabur.app` (Your Backend URL)

---

## 🔐 Environment Variables (Required)

### Backend Service Variables
| Key | Value |
| :--- | :--- |
| `GOOGLE_CLIENT_ID` | (From Google Cloud Console) |
| `GOOGLE_CLIENT_SECRET` | (From Google Cloud Console) |
| `GEMINI_API_KEY` | (Optional, From Google AI Studio) |
| `GM_EMAILS` | (comma-separated admin emails) |
| `SECRET_KEY` | (Random string) |
| `FRONTEND_URL` | `https://martian-app.zeabur.app` (Your Frontend URL - for CORS) |

---

## 🔄 Google OAuth Update
Go to Google Cloud Console > APIs & Services > Credentials:
1.  **Authorized Javascript Origins**: `https://martian-app.zeabur.app`
2.  **Authorized Redirect URI**: `https://martian-api.zeabur.app/auth/callback` (Note: Callback goes to Backend!)

---

## 🛠️ Local Development
- **Backend**: `uvicorn app.main:app --reload --port 8000`
- **Frontend**: `cd frontend && npm run dev`
- Open `http://localhost:3000`

---

## ☁️ Alternative: Google Cloud Run (Taiwan Region)

Cloud Run offers **lower latency** for Taiwan users via `asia-east1` region and integrates with Google AI Pro's **$10/month GCP credit**.

### Why Cloud Run?
| Advantage | Detail |
|-----------|--------|
| **Taiwan Region** | `asia-east1` (彰化) = ~10ms latency vs. Zeabur Singapore ~50ms |
| **Cold Start** | ~1-3s (faster than Zeabur's ~2-5s) |
| **Free Tier** | 2M requests/month, 360K GB-seconds |
| **AI Pro Credit** | $10/month GCP credit covers most small projects |

### Prerequisites
1. Google Cloud account with billing enabled
2. `gcloud` CLI installed: `brew install google-cloud-sdk` (Mac) or [install guide](https://cloud.google.com/sdk/docs/install)
3. Docker installed (for local builds, optional)

---

### Step 1: Setup GCP Project

```bash
# Login & set project
gcloud auth login
gcloud projects create martian-invest --name="Martian Investment"
gcloud config set project martian-invest

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Set default region
gcloud config set run/region asia-east1
```

---

### Step 2: Deploy Backend (FastAPI)

#### Option A: Direct Source Deploy (Recommended)
```bash
# From repo root
gcloud run deploy martian-backend \
  --source . \
  --region asia-east1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8000 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 3 \
  --set-env-vars "GOOGLE_CLIENT_ID=xxx,GOOGLE_CLIENT_SECRET=xxx,SECRET_KEY=xxx,FRONTEND_URL=https://martian-app-xxx.run.app"
```

#### Option B: Dockerfile Deploy
Create `Dockerfile` in repo root:
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen

COPY app/ ./app/
COPY project_tw/ ./project_tw/

# Pre-warm data (Git-versioned)
COPY app/data/ ./app/data/

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
gcloud run deploy martian-backend \
  --source . \
  --region asia-east1 \
  --allow-unauthenticated
```

---

### Step 3: Deploy Frontend (Next.js)

```bash
cd frontend

gcloud run deploy martian-frontend \
  --source . \
  --region asia-east1 \
  --platform managed \
  --allow-unauthenticated \
  --port 3000 \
  --memory 512Mi \
  --set-env-vars "NEXT_PUBLIC_API_URL=https://martian-backend-xxx-de.a.run.app"
```

> [!NOTE]
> Replace `xxx` with your actual Cloud Run service URLs after first deploy.

---

### Step 4: Database Persistence Strategy

Cloud Run containers are **ephemeral** (like Zeabur). Choose a persistence strategy:

#### Option A: Git-Backup Mode (Free, Current Approach)
Keep using the existing Git-backup mechanism:
- SQLite DB lives in container
- Daily backup pushes to GitHub
- On redeploy, DB restores from Git

**Pros**: Free, no config changes  
**Cons**: Data loss window = time since last backup

#### Option B: Cloud SQL (Recommended for Production)
```bash
# Create PostgreSQL instance (~$7/month for db-f1-micro)
gcloud sql instances create martian-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=asia-east1

# Create database
gcloud sql databases create martian --instance=martian-db

# Get connection string
gcloud sql instances describe martian-db --format="value(connectionName)"
# Output: martian-invest:asia-east1:martian-db

# Update backend to use PostgreSQL (requires code change)
```

#### Option C: Cloud Storage for SQLite (Hybrid)
Mount GCS bucket as filesystem using `gcsfuse`:
```bash
# Create bucket
gcloud storage buckets create gs://martian-data --location=asia-east1

# In Dockerfile, add gcsfuse and mount script
# Requires custom entrypoint to sync DB from GCS on startup
```

---

### Step 5: Environment Variables via Secret Manager

For sensitive values, use Secret Manager:

```bash
# Create secrets
echo -n "your-google-client-secret" | gcloud secrets create GOOGLE_CLIENT_SECRET --data-file=-
echo -n "your-secret-key" | gcloud secrets create SECRET_KEY --data-file=-

# Grant Cloud Run access
gcloud secrets add-iam-policy-binding GOOGLE_CLIENT_SECRET \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Deploy with secrets
gcloud run deploy martian-backend \
  --set-secrets="GOOGLE_CLIENT_SECRET=GOOGLE_CLIENT_SECRET:latest,SECRET_KEY=SECRET_KEY:latest"
```

---

### Step 6: Custom Domain (Optional)

```bash
# Map custom domain
gcloud run domain-mappings create \
  --service martian-frontend \
  --domain martian.yourdomain.com \
  --region asia-east1

# Get DNS records to configure
gcloud run domain-mappings describe \
  --domain martian.yourdomain.com \
  --region asia-east1
```

---

### Step 7: Update Google OAuth

Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials):

1. **Authorized JavaScript Origins**:
   - `https://martian-frontend-xxx-de.a.run.app`
   - `https://martian.yourdomain.com` (if custom domain)

2. **Authorized Redirect URIs**:
   - `https://martian-backend-xxx-de.a.run.app/auth/callback`

---

### Cost Estimation

| Component | Monthly Cost |
|-----------|-------------|
| Cloud Run (Backend) | ~$0-5 (free tier covers most) |
| Cloud Run (Frontend) | ~$0-3 (static + SSR) |
| Cloud SQL (optional) | ~$7-10 (db-f1-micro) |
| **Total** | **$0-18/month** |

With Google AI Pro's **$10 credit**, effective cost = **$0-8/month**.

---

### Migration Checklist

- [ ] Create GCP project & enable APIs
- [ ] Deploy Backend to Cloud Run
- [ ] Deploy Frontend to Cloud Run
- [ ] Configure environment variables
- [ ] Update OAuth redirect URIs
- [ ] Test login flow end-to-end
- [ ] Configure database persistence (Git-backup or Cloud SQL)
- [ ] Set up monitoring (Cloud Run → Logs)
- [ ] (Optional) Configure custom domain
- [ ] (Optional) Set up Cloud Scheduler for daily backup

---

### Rollback Plan

If Cloud Run doesn't work out:
1. Zeabur deployment remains intact (don't delete it during testing)
2. Simply switch DNS/OAuth back to Zeabur URLs
3. Cloud Run services can be deleted with: `gcloud run services delete martian-backend`
