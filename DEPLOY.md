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
    - **Domain**: Generate one (e.g., `martian-ui.zeabur.app`). **This is your App URL.**
4.  **Enviroment Variables** (In Frontend Service):
    - `NEXT_PUBLIC_API_URL`: `https://martian-api.zeabur.app` (Your Backend URL)

---

## 🔐 Environment Variables (Required)

### Backend Service Variables
| Key | Value |
| :--- | :--- |
| `GOOGLE_CLIENT_ID` | (From Google Cloud Console) |
| `GOOGLE_CLIENT_SECRET` | (From Google Cloud Console) |
| `GEMINI_API_KEY` | (From Google AI Studio) |
| `GM_EMAILS` | (comma-separated admin emails) |
| `SECRET_KEY` | (Random string) |
| `FRONTEND_URL` | `https://martian-ui.zeabur.app` (Your Frontend URL - for CORS) |

---

## 🔄 Google OAuth Update
Go to Google Cloud Console > APIs & Services > Credentials:
1.  **Authorized Javascript Origins**: `https://martian-ui.zeabur.app`
2.  **Authorized Redirect URI**: `https://martian-api.zeabur.app/auth/callback` (Note: Callback goes to Backend!)

---

## 🛠️ Local Development
- **Backend**: `uvicorn app.main:app --reload --port 8000`
- **Frontend**: `cd frontend && npm run dev`
- Open `http://localhost:3000`
