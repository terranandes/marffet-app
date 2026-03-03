

# Tier limits
FREE_MAX_GROUPS = 11
FREE_MAX_TARGETS_PER_GROUP = 50
FREE_MAX_TX_PER_TARGET = 100

PREMIUM_MAX_GROUPS = 20
PREMIUM_MAX_TARGETS_PER_GROUP = 100
PREMIUM_MAX_TX_PER_TARGET = 500

VIP_MAX_GROUPS = 30
VIP_MAX_TARGETS_PER_GROUP = 200
VIP_MAX_TX_PER_TARGET = 1000

GM_MAX_GROUPS = 1000
GM_MAX_TARGETS_PER_GROUP = 1000
GM_MAX_TX_PER_TARGET = 10000

# --- Global Name Cache ---
STOCK_NAME_CACHE = {}

# Manual Supplementary Cache for stocks missing from Excel but essential
# Used to bypass unreliable API fetches in Production (Zeabur)
SUPPLEMENTARY_NAME_CACHE = {
    "6533": "晶心科技",
    "6533.TW": "晶心科技",
    "6533.TWO": "晶心科技",
    "00950B": "凱基A級公司債",     # API returns English
    "00980D": "主動聯博投等入息",
    # 00981A removed - API fetches correct name "主動統一台股增長"
}
