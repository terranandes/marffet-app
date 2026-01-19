# Fix: Zeabur Login CORS Error

## Problem
Login fails on `https://martian-app.zeabur.app` with CORS error:
```
Access to fetch at 'https://accounts.google.com/...' has been blocked by CORS policy
```

## Root Cause
The Google OAuth application is not configured to allow redirects from the Zeabur domain.

## Solution

### Step 1: Add Zeabur Callback URL to Google Cloud Console

1. Go to [Google Cloud Console - Credentials](https://console.cloud.google.com/apis/credentials)
2. Find your OAuth 2.0 Client ID: `1009725210430-ous6uqh499d5k8afqgv92ap61342q56m.apps.googleusercontent.com`
3. Click **Edit** on the OAuth client
4. Under **Authorized redirect URIs**, add:
   ```
   https://martian-app.zeabur.app/auth/callback
   ```
5. **Save** the changes

### Step 2: Update Zeabur Environment Variables

In your Zeabur project settings, ensure these environment variables are set:

#### Backend Service
```bash
GOOGLE_CLIENT_ID=1009725210430-ous6uqh499d5k8afqgv92ap61342q56m.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
SECRET_KEY=WISH_MARTIAN_A_GREAT_SECRET
GM_EMAILS=terranfund@gmail.com,terranandes@gmail.com
FRONTEND_URL=https://martian-app.zeabur.app
GITHUB_REPO=terranandes/martian
GITHUB_TOKEN=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
```

#### Frontend Service
```bash
NEXT_PUBLIC_API_URL=https://martian-app.zeabur.app
```

### Step 3: Redeploy (if needed)

After updating environment variables, Zeabur should automatically redeploy. If not:
1. Go to Zeabur Dashboard
2. Click **Redeploy** on both services

### Step 4: Test

1. Visit `https://martian-app.zeabur.app`
2. Click **Sign in with Google**
3. Login should now work without CORS errors

## Additional Notes

- **Guest Mode** is also available as a fallback (no login required)
- The OAuth callback URL pattern is: `{BACKEND_URL}/auth/callback`
- For local development, keep `http://localhost:8000/auth/callback` in the authorized URIs

## Verification Checklist

- [ ] Added `https://martian-app.zeabur.app/auth/callback` to Google OAuth
- [ ] Set `FRONTEND_URL=https://martian-app.zeabur.app` in Zeabur backend env
- [ ] Set `NEXT_PUBLIC_API_URL=https://martian-app.zeabur.app` in Zeabur frontend env
- [ ] Redeployed services
- [ ] Tested login flow
