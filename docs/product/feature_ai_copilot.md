# AI Copilot — Feature Specification

**Date**: 2026-02-17
**Owner**: [SPEC] Agent
**Status**: Production

---

## 1. Overview

The **AI Copilot** is a floating chat widget powered by **Google Gemini**. It provides contextual investment advice based on the user's portfolio data. It supports two personality tiers: **Free** (educational, encouraging) and **Premium** (ruthless, data-driven wealth manager).

---

## 2. Tier System

| Tier        | Personality                 | Key Traits                        |
|:----------- |:--------------------------- |:--------------------------------- |
| **Free**    | Mars AI (Investment Educator) | Encouraging, patient, educational |
| **Premium** | Mars AI (Wealth Manager)    | Precise, data-driven, action-oriented |

### Free Tier Prompt

> *"You are Mars AI (Free Tier), an investment educator designed to build CONFIDENCE. Explain WHY the 'Mars Strategy' (Buying Top 50 Past Performers & Holding) works. Focus on the philosophy."*

### Premium Tier Prompt

> *"You are Mars AI (Premium Tier), a ruthless wealth manager designed to enforce DISCIPLINE. Optimize returns using the 'MoneyCome' methodology (CAGR & Volatility). If a stock is overheated (+20% vs SMA) or drops out of Top 50, strongly suggest selling."*

---

## 3. Frontend

**Component**: `frontend/src/components/AICopilot.tsx` (189 lines)
**Activation**: Floating button on all pages (bottom-right corner)

### UI Elements

1. **Toggle Button** — Expand/collapse the chat panel
2. **Chat Panel** — Animated slide-in panel with message history
3. **API Key Input** — Users can enter their own Gemini key for higher rate limits
4. **Message Bubbles** — User (right) and AI (left) styled messages
5. **Context Injection** — Portfolio summary is automatically included

### Props Interface

```typescript
interface AICopilotProps {
    user: any;
    portfolioContext?: string;  // JSON summary of user's portfolio
}
```

### Key Functions

| Function        | Purpose                                    |
|:--------------- |:------------------------------------------ |
| `sendMessage()` | POST to `/api/chat` with message + context |
| `saveApiKey()`  | Save Gemini API key to localStorage        |

---

## 4. Backend API

**Endpoint**: `POST /api/chat`
**Auth**: None required (API key-based)

### Request Schema

```json
{
    "message": "Should I sell TSMC?",
    "context": "Portfolio: 2330 (50 shares, avg 580), 2454 (100 shares, avg 970)...",
    "apiKey": "AIzaSy...",
    "isPremium": false
}
```

### Response Schema

```json
{
    "response": "Based on TSMC's historical CAGR of 15.2%..."
}
```

### Model Selection Strategy

1. **Primary**: `gemini-3-flash-preview` (latest)
2. **Fallback**: Auto-discovery via `client.models.list()`
3. **Priority Order**: gemini-1.5-pro → gemini-pro → gemini-1.5-flash → gemini-1.0-pro
4. **Graceful**: Tries all available models before returning an error

### API Key Resolution

1. **Client key** (user provides in Settings Modal → saved to localStorage)
2. **Server key** (fallback to `GEMINI_API_KEY` environment variable)
3. **Error** if neither exists

---

## 5. Architecture

```
User types message ──▶ AICopilot.sendMessage()
                            │
                            ├── Inject portfolioContext (from parent page)
                            ├── Inject isPremium flag
                            └── POST /api/chat
                                    │
                                    ├── Select system prompt (Free / Premium)
                                    ├── Construct conversation history
                                    └── genai.Client.generate_content()
                                            │
                                            ├── Success → Return response text
                                            └── Failure → Auto-discover model → Retry
```

---

## 6. Security

- API keys are stored in **localStorage** only (never sent to our server for storage)
- The server has a fallback `GEMINI_API_KEY` env var for users without their own key
- Context is sanitized before injection (no raw database queries)
