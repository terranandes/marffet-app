import { createApp, ref, onMounted, computed, watch, nextTick } from '/static/vendor/vue.esm-browser.js'

import CONFIG from '/static/js/config.js'

const originalFetch = window.fetch;
const apiFetch = async (url, options = {}) => {
    let finalUrl = url;
    if (typeof url === 'string' && url.startsWith('/')) {
        finalUrl = CONFIG.API_BASE + url;
    }
    const finalOptions = { ...options, credentials: 'include' };
    return originalFetch(finalUrl, finalOptions);
};

createApp({
    setup() {
        const currentUser = ref(null); // Auth State
        const backendUrl = ref(CONFIG.API_BASE ? 'Remote API' : 'Local Host');
        const currentTab = ref('mars');
        const rawMarsData = ref([]);
        const rawRaceData = ref([]);
        const marsList = ref([]); // Processed
        const detailStock = ref(null); // Selected for Modal
        const cbInput = ref('6533');
        const cbResult = ref(null);
        const loadingCB = ref(false);

        // ========== GUEST MODE ==========
        const isGuest = computed(() => currentUser.value === null || currentUser.value?.is_guest === true);
        const GUEST_LIMITS = {
            maxGroups: 3,
            maxTargetsPerGroup: 10,
            maxTransactionsPerTarget: 10
        };
        const GUEST_STORAGE_KEY = 'martian_guest_portfolio';

        // Guest localStorage helpers
        const loadGuestData = () => {
            try {
                const data = localStorage.getItem(GUEST_STORAGE_KEY);
                return data ? JSON.parse(data) : { groups: [], nextGroupId: 1, nextTargetId: 1, nextTxId: 1 };
            } catch (e) {
                console.error('Failed to load guest data:', e);
                return { groups: [], nextGroupId: 1, nextTargetId: 1, nextTxId: 1 };
            }
        };
        const saveGuestData = (data) => {
            try {
                localStorage.setItem(GUEST_STORAGE_KEY, JSON.stringify(data));
            } catch (e) {
                console.error('Failed to save guest data:', e);
                addNotification('⚠️ Failed to save data locally');
            }
        };
        const guestData = ref(loadGuestData());

        // ========== NOTIFICATIONS SYSTEM ==========
        // ========== NOTIFICATIONS SYSTEM ==========
        const showNotifications = ref(false);
        const notifications = ref([]);
        const unreadCount = computed(() => notifications.value.filter(n => !n.is_read).length);

        const fetchNotifications = async () => {
            if (!currentUser.value) return;
            try {
                // Calling /api/notifications triggers the Lazy RuthlessManager check
                const res = await apiFetch('/api/notifications');
                if (res.ok) {
                    const data = await res.json();
                    // Merge/Update logic:
                    // We simply replace for Prototype, or we could diff.
                    // The backend returns only UNREAD by default? 
                    // Wait, spec said `get_unread_notifications`.
                    // So we should maybe append or just set?
                    // Let's set it, but we might lose "read" history if we only fetch unread.
                    // UI Requirement: Show unread. If I read it, it goes away? 
                    // Or stays as "read"?
                    // Backend `get_unread_notifications` only returns unread.
                    // So if I mark read, it disappears on next poll.
                    // This is acceptable for "Contractive" UI.
                    notifications.value = data.map(n => ({
                        ...n,
                        time: new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                    }));

                    if (data.length > 0 && !showNotifications.value) {
                        // Auto-badge is handled by unreadCount. 
                        // Auto-open might be annoying if frequent?
                        // Let's NOT auto-open, just badge.
                    }
                }
            } catch (e) {
                console.error('Fetch notifications error:', e);
            }
        };

        const markAsRead = async (n) => {
            if (n.is_read) return;
            try {
                // Optimistic UI update
                n.is_read = 1;
                // Call Backend
                await apiFetch(`/api/notifications/${n.id}/read`, { method: 'POST' });
                // Re-fetch to sync (it will disappear from list if backend only returns unread)
                // Let's wait a bit or just let the next poll handle removal?
                // Better UX: Fade out or keep as read until close?
                // Current logic: simple list.
            } catch (e) {
                console.error('Mark read error:', e);
                n.is_read = 0; // Revert
            }
        };

        const markAllRead = async () => {
            notifications.value.forEach(n => markAsRead(n));
        };

        const clearNotifications = () => {
            markAllRead(); // Effectively clears them since backend only stores unread status
            showNotifications.value = false;
        };

        // Polling
        let notifInterval = null;
        const startNotifPolling = () => {
            if (notifInterval) clearInterval(notifInterval);
            fetchNotifications(); // Initial fetch
            notifInterval = setInterval(fetchNotifications, 60000); // Poll every 60s
        };

        // Legacy/Unused helpers replaced: deleteNotification, addNotification, checkSystemAlerts
        // We keep addNotification purely for local system messages if needed, but likely unused now.
        const addNotification = (msg) => { console.log('Local notif:', msg); };



        // ========== CB PORTFOLIO ==========
        const portfolioCBs = ref([]);
        const loadingPortfolioCBs = ref(false);
        const fetchPortfolioCBs = async () => {
            loadingPortfolioCBs.value = true;
            try {
                const res = await apiFetch('/api/cb/portfolio');
                if (res.ok) portfolioCBs.value = await res.json();
            } catch (e) {
                console.error(e);
                addNotification('❌ Failed to load Portfolio CBs');
            } finally {
                loadingPortfolioCBs.value = false;
            }
        };

        // ========== I18N SYSTEM ==========
        const availableLanguages = [
            { code: 'en', name: 'English' },
            { code: 'zh-TW', name: '繁體中文' },
            { code: 'zh-CN', name: '简体中文' }
        ];

        const translations = {
            en: {
                // Nav
                nav_mars: 'Mars Strategy',
                nav_race: 'Bar Chart Race',
                nav_portfolio: 'Portfolio',
                nav_trend: 'Trend',
                nav_ladder: 'Cash Ladder',
                nav_cb: 'CB Strategy',
                nav_myrace: 'My Race',
                // Portfolio Header
                p_sync_div: 'Sync Dividends',
                p_new_group: 'New Group',
                p_div_cash: 'Dividend Cash',
                p_payments: 'payments',
                // Dashboard
                d_mkt_val: 'Market Value',
                d_realized: 'Realized P/L',
                d_unrealized: 'Unrealized P/L',
                // Inputs
                in_group_name: 'Group name',
                in_create: 'Create',
                in_no_groups: 'No groups yet. Create one above.',
                in_code: 'Stock Code',
                in_name: 'Stock Name (opt)',
                in_add_stock: 'Add Stock',
                // Table Headers
                th_stock: 'Stock',
                th_price: 'Price/Change',
                th_shares: 'Shares',
                th_cost: 'Cost/Avg',
                th_mkt: 'Market Val',
                th_realized: 'Realized',
                th_unrealized: 'Unrealized',
                th_tx_count: 'Tx Count',
                th_actions: 'Actions',
                // Table Content
                tx_add: '+Trade',
                tx_del: 'Delete',
                no_stocks: 'No stocks in this group.',
                // Modals
                m_new_tx: 'New Transaction',
                m_edit_tx: 'Edit Transaction',
                m_buy: 'Buy',
                m_sell: 'Sell',
                m_shares: 'Shares',
                m_price: 'Price',
                m_date: 'Date',
                m_confirm: 'Confirm',
                m_update: 'Update',
                m_cancel: 'Cancel',
                m_history: 'Transaction History',
                m_add: 'Add',
                m_close: 'Close',
                h_date: 'Date',
                h_type: 'Type',
                h_total: 'Total',
                // Settings
                s_title: 'Settings',
                s_lang: 'Language',
                s_region: 'Region',
                s_gm: 'GM Mode',
                s_api: 'Gemini API Key',
                s_save: 'Save',
                // Trend
                trend_title: 'Portfolio Trend', trend_refresh: 'Refresh', trend_net_inv: 'Net Investment Over Time',
                trend_asset_groups: 'Asset Groups', trend_stock: 'Stock', trend_etf: 'ETF', trend_cb: 'CB',
                // CB
                cb_title: 'My Portfolio CBs', cb_analyzer: 'CB Arbitrage Analyzer', cb_analyze: 'Analyze',
                cb_scanning: 'Scanning...', cb_premium: 'Premium Rate', cb_stock: 'Stock', cb_cb: 'CB', cb_conv: 'Conv',
                // Race
                race_title: 'Dynamic Wealth Race', race_play: 'Play', race_pause: 'Pause', race_reset: 'Reset',
                race_wealth: 'Final Wealth ($)', race_cagr: 'Performance (CAGR %)',
                // Leaderboard
                lb_rank: 'Rank', lb_id: 'ID', lb_name: 'Name', lb_sim_final: 'Simulated Final ($)',
                lb_cagr: 'CAGR %', lb_vol: 'Volatility %',
                // Notifications
                n_title: 'Notifications', n_read_all: 'Mark all read', n_clear: 'Clear', n_empty: 'No notifications',
                // Login
                l_title: 'Martian Investment System', l_subtitle: 'Secure Access • Multi-User Environment', l_google: 'Sign in with Google', l_init: 'Initializing...',
                // Chat
                c_title: 'Mars Copilot', c_thinking: 'Thinking...', c_placeholder: 'Ask about your portfolio...',
                // Simulation
                sim_title: 'Simulation Settings', sim_start: 'Start Year', sim_cap: 'Initial Capital'
            },
            'zh-TW': {
                nav_mars: '賽局回測',
                nav_race: '動態競賽',
                nav_portfolio: '投資組合',
                nav_trend: '資產趨勢',
                nav_ladder: '現金階梯',
                nav_cb: '可轉債',
                nav_myrace: '我的競賽',
                p_sync_div: '同步股息',
                p_new_group: '新增群組',
                p_div_cash: '股息現金',
                p_payments: '筆',
                d_mkt_val: '總市值',
                d_realized: '已實現損益',
                d_unrealized: '未實現損益',
                in_group_name: '群組名稱',
                in_create: '建立',
                in_no_groups: '尚無群組',
                in_code: '股票代號',
                in_name: '股票名稱 (選填)',
                in_add_stock: '新增',
                th_stock: '股名/代號',
                th_price: '股價/漲跌',
                th_shares: '持有股數',
                th_cost: '成本/均價',
                th_mkt: '市值',
                th_realized: '已實現',
                th_unrealized: '未實現',
                th_tx_count: '交易筆數',
                th_actions: '操作',
                tx_add: '+交易',
                tx_del: '刪除',
                no_stocks: '此群組無股票',
                m_new_tx: '新增交易',
                m_edit_tx: '編輯交易',
                m_buy: '買入',
                m_sell: '賣出',
                m_shares: '股數',
                m_price: '單價',
                m_date: '日期',
                m_confirm: '確認',
                m_update: '更新',
                m_cancel: '取消',
                m_history: '交易紀錄',
                m_add: '新增',
                m_close: '關閉',
                h_date: '日期',
                h_type: '類別',
                h_total: '總額',
                s_title: '設定',
                s_lang: '語言',
                s_region: '地區',
                s_gm: 'GM 模式',
                s_api: 'API 金鑰',
                s_save: '儲存',
                // Trend
                trend_title: '資產趨勢', trend_refresh: '重新整理', trend_net_inv: '淨投入資金趨勢',
                trend_asset_groups: '資產類別', trend_stock: '股票', trend_etf: 'ETF', trend_cb: '可轉債',
                // CB
                cb_title: '我的可轉債', cb_analyzer: '可轉債套利分析', cb_analyze: '分析',
                cb_scanning: '掃描中...', cb_premium: '溢價率', cb_stock: '現股', cb_cb: '可轉債', cb_conv: '轉換價',
                // Race
                race_title: '動態財富競賽', race_play: '播放', race_pause: '暫停', race_reset: '重置',
                race_wealth: '最終財富 ($)', race_cagr: '年化報酬率 (CAGR %)',
                // Leaderboard
                lb_rank: '排名', lb_id: '代號', lb_name: '名稱', lb_sim_final: '模擬最終金額 ($)',
                lb_cagr: '年化報酬率', lb_vol: '波動率 %',
                // Notifications
                n_title: '通知', n_read_all: '全部已讀', n_clear: '清除', n_empty: '暫無通知',
                // Login
                l_title: '火星投資系統', l_subtitle: '安全存取 • 多用戶環境', l_google: 'Google 登入', l_init: '初始化中...',
                // Chat
                c_title: '火星副駕駛', c_thinking: '思考中...', c_placeholder: '詢問關於您的投資組合...',
                // Simulation
                sim_title: '模擬設定', sim_start: '開始年份', sim_cap: '初始資金'
            },
            'zh-CN': {
                nav_mars: '赛局回测',
                nav_race: '动态竞赛',
                nav_portfolio: '投资组合',
                nav_trend: '资产趋势',
                nav_ladder: '现金阶梯',
                nav_cb: '可转债',
                nav_myrace: '我的竞赛',
                p_sync_div: '同步股息',
                p_new_group: '新增群组',
                p_div_cash: '股息现金',
                p_payments: '笔',
                d_mkt_val: '总市值',
                d_realized: '已实现损益',
                d_unrealized: '未实现损益',
                in_group_name: '群组名称',
                in_create: '建立',
                in_no_groups: '尚无群组',
                in_code: '股票代号',
                in_name: '股票名称 (选填)',
                in_add_stock: '新增',
                th_stock: '股名/代号',
                th_price: '股价/涨跌',
                th_shares: '持有股数',
                th_cost: '成本/均价',
                th_mkt: '市值',
                th_realized: '已实现',
                th_unrealized: '未实现',
                th_tx_count: '交易笔数',
                th_actions: '操作',
                tx_add: '+交易',
                tx_del: '删除',
                no_stocks: '此群组无股票',
                m_new_tx: '新增交易',
                m_edit_tx: '编辑交易',
                m_buy: '买入',
                m_sell: '卖出',
                m_shares: '股数',
                m_price: '单价',
                m_date: '日期',
                m_confirm: '确认',
                m_update: '更新',
                m_cancel: '取消',
                m_history: '交易纪录',
                m_add: '新增',
                m_close: '关闭',
                h_date: '日期',
                h_type: '类别',
                h_total: '总额',
                s_title: '设置',
                s_lang: '语言',
                s_region: '地区',
                s_gm: 'GM 模式',
                s_api: 'API 密钥',
                s_save: '保存',
                // Trend
                trend_title: '资产趋势', trend_refresh: '刷新', trend_net_inv: '净投入资金趋势',
                trend_asset_groups: '资产类别', trend_stock: '股票', trend_etf: 'ETF', trend_cb: '可转债',
                // CB
                cb_title: '我的可转债', cb_analyzer: '可转债套利分析', cb_analyze: '分析',
                cb_scanning: '扫描中...', cb_premium: '溢价率', cb_stock: '现股', cb_cb: '可转债', cb_conv: '转换价',
                // Race
                race_title: '动态财富竞赛', race_play: '播放', race_pause: '暂停', race_reset: '重置',
                race_wealth: '最终财富 ($)', race_cagr: '年化回报率 (CAGR %)',
                // Leaderboard
                lb_rank: '排名', lb_id: '代号', lb_name: '名称', lb_sim_final: '模拟最终金额 ($)',
                lb_cagr: '年化回报率', lb_vol: '波动率 %',
                // Notifications
                n_title: '通知', n_read_all: '全部已读', n_clear: '清除', n_empty: '暂无通知',
                // Login
                l_title: '火星投资系统', l_subtitle: '安全访问 • 多用户环境', l_google: 'Google 登录', l_init: '初始化中...',
                // Chat
                c_title: '火星副驾驶', c_thinking: '思考中...', c_placeholder: '询问关于您的投资组合...',
                // Simulation
                sim_title: '模拟设置', sim_start: '开始年份', sim_cap: '初始资金'
            }
        };

        const detectLanguage = () => {
            const browserLang = navigator.language;
            if (browserLang.toLowerCase().includes('cn')) return 'zh-CN';
            if (browserLang.toLowerCase().includes('tw') || browserLang.toLowerCase().includes('hk')) return 'zh-TW';
            return 'en';
        };

        // ========== SETTINGS SYSTEM ==========
        const showSettings = ref(false);
        const defaultSettings = {
            region: 'TW', gmMode: false, defaultTab: 'mars', apiKey: '', language:
                detectLanguage()
        };
        const appSettings = ref({ ...defaultSettings });

        // ========== FEEDBACK SYSTEM ==========
        const feedbackForm = ref({ category: '', type: 'bug', message: '' });
        const feedbackSubmitting = ref(false);
        const feedbackSuccess = ref(false);

        const submitFeedback = async () => {
            if (!feedbackForm.value.category || !feedbackForm.value.message) return;

            feedbackSubmitting.value = true;
            feedbackSuccess.value = false;

            try {
                const res = await apiFetch('/api/feedback', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        feature_category: feedbackForm.value.category,
                        feedback_type: feedbackForm.value.type,
                        message: feedbackForm.value.message
                    })
                });

                if (res.ok) {
                    feedbackSuccess.value = true;
                    feedbackForm.value = { category: '', type: 'bug', message: '' };
                    setTimeout(() => { feedbackSuccess.value = false; }, 3000);
                }
            } catch (e) {
                console.error('Feedback submit error:', e);
            } finally {
                feedbackSubmitting.value = false;
            }
        };

        const t = (key) => {
            const lang = appSettings.value.language || 'en';
            return translations[lang]?.[key] || translations['en'][key] || key;
        };

        // ========== AI COPILOT ==========
        const showChat = ref(false);
        const chatInput = ref('');
        const isChatLoading = ref(false);
        const chatHistory = ref([
            { role: 'model', text: 'Hello! I am Mars AI 🤖. How can I help you with your investments today?' }
        ]);


        const sendMessage = async () => {
            if (!chatInput.value.trim()) return;
            if (!appSettings.value.apiKey) {
                chatHistory.value.push({ role: 'model', text: 'Please set your Gemini API Key in Settings ⚙️ to chat.' });
                return;
            }

            const userMsg = chatInput.value;
            chatHistory.value.push({ role: 'user', text: userMsg });
            chatInput.value = '';
            isChatLoading.value = true;

            // Build Context with individual stock details
            const holdingsDetail = groupTargets.value.map(t => {
                const s = t.summary || {};
                return `    - ${t.name || t.stock_id}: ${s.total_shares || 0} shares @ avg $${(s.avg_cost || 0).toFixed(2)}, ` +
                    `Market: ${formatCurrency(s.market_value || 0)}, P/L: ${formatCurrency(s.unrealized_pnl || 0)}`;
            }).join('\n');

            const context = `
        Portfolio Summary:
        - Total Groups: ${portfolioGroups.value.length}
        - Total Stocks: ${groupTargets.value.length}
        - Market Value: ${formatCurrency(groupStats.value?.marketValue || 0)}
        - Total Cost: ${formatCurrency(groupStats.value?.totalCost || 0)}
        - Unrealized P/L: ${formatCurrency(groupStats.value?.unrealized || 0)} (${groupStats.value?.unrealizedPct?.toFixed(1) || 0}%)
        - Realized P/L: ${formatCurrency(groupStats.value?.realized || 0)}
        - Premium User: ${isPremium.value}

        Individual Holdings:
${holdingsDetail || '        (No holdings yet)'}
        `;

            try {
                const res = await apiFetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: userMsg,
                        context: context,
                        apiKey: appSettings.value.apiKey,
                        isPremium: isPremium.value
                    })
                });
                const data = await res.json();
                if (res.ok) {
                    chatHistory.value.push({ role: 'model', text: data.response });
                } else {
                    chatHistory.value.push({ role: 'model', text: `Error: ${data.error}` });
                }
            } catch (e) {
                chatHistory.value.push({ role: 'model', text: 'Network Error.' });
            } finally {
                isChatLoading.value = false;
                // Scroll to bottom
                nextTick(() => {
                    const container = document.getElementById('chat-container');
                    if (container) container.scrollTop = container.scrollHeight;
                });
            }
        };

        // ========== PREMIUM NOTIFICATIONS ==========
        const fetchStrategyAlerts = async () => {
            if (!isPremium.value) return; // Premium only
            try {
                const res = await apiFetch('/api/notifications/check');
                if (res.ok) {
                    const alerts = await res.json();
                    alerts.forEach(alert => {
                        // Add to notification list with special icon
                        notifications.value.unshift({
                            message: `${alert.message}`,
                            time: new Date().toLocaleTimeString(),
                            read: false,
                            type: 'strategy'
                        });
                    });
                    if (alerts.length > 0) addNotification(`Found ${alerts.length} strategy alerts! 🔔`);
                }
            } catch (e) {
                console.error('Strategy alerts fetch error:', e);
            }
        };

        const loadSettings = () => {
            try {
                const saved = localStorage.getItem('martian_settings');
                if (saved) appSettings.value = { ...defaultSettings, ...JSON.parse(saved) };

                // Check alerts on load if premium
                if (appSettings.value.gmMode) fetchStrategyAlerts();
            } catch (e) { console.error('Load settings error:', e); }
        };
        const saveSettings = () => {
            try { localStorage.setItem('martian_settings', JSON.stringify(appSettings.value)); }
            catch (e) { console.error('Save settings error:', e); }
        };
        const toggleGMMode = () => { appSettings.value.gmMode = !appSettings.value.gmMode; saveSettings(); };
        // Premium logic:
        // - GM users: ONLY controlled by gmMode toggle (for testing both tiers)
        // - Regular users: auto-premium if subscribed
        const isPremium = computed(() => {
            if (currentUser.value?.is_admin) {
                return appSettings.value.gmMode; // GM can toggle for testing
            }
            return currentUser.value?.subscription_tier > 0; // Regular users: subscription-based
        });

        // ========== ADMIN DASHBOARD (GM ONLY) ==========
        const adminMetrics = ref({});
        const adminLoading = ref(false);
        const adminError = ref(null);

        const fetchAdminMetrics = async () => {
            adminLoading.value = true;
            adminError.value = null;
            try {
                const res = await apiFetch('/api/admin/metrics');
                if (res.status === 403) {
                    adminError.value = 'Access Denied: Admin privileges required';
                } else if (res.status === 401) {
                    adminError.value = 'Please login first';
                } else if (res.ok) {
                    adminMetrics.value = await res.json();
                } else {
                    adminError.value = 'Failed to fetch metrics';
                }
            } catch (e) {
                adminError.value = 'Network error';
            } finally {
                adminLoading.value = false;
            }
        };

        // ========== FEEDBACK ADMIN PANEL (GM ONLY) ==========
        const feedbackList = ref([]);
        const feedbackStats = ref({});

        const fetchFeedbackList = async () => {
            try {
                const [listRes, statsRes] = await Promise.all([
                    apiFetch('/api/feedback'),
                    apiFetch('/api/feedback/stats')
                ]);
                if (listRes.ok) feedbackList.value = await listRes.json();
                if (statsRes.ok) feedbackStats.value = await statsRes.json();
            } catch (e) {
                console.error('Fetch feedback error:', e);
            }
        };

        const updateFeedbackStatus = async (id, status) => {
            try {
                await apiFetch(`/api/feedback/${id}`, {
                    method: 'PATCH',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ status })
                });
                // Refresh stats after update
                const statsRes = await apiFetch('/api/feedback/stats');
                if (statsRes.ok) feedbackStats.value = await statsRes.json();
            } catch (e) {
                console.error('Update feedback error:', e);
            }
        };

        const copyFeedback = (fb) => {
            const text = `## User Feedback Report
**ID:** ${fb.id}
**Type:** ${fb.feedback_type}
**Feature:** ${fb.feature_category}
**Status:** ${fb.status}
**From:** ${fb.user_email || 'Anonymous'}
**Date:** ${fb.created_at?.substring(0, 10)}

**Message:**
${fb.message}

---
Please analyze this feedback and determine if it's a true bug.`;

            navigator.clipboard.writeText(text).then(() => {
                alert('Feedback copied! Paste to AI agent for review.');
            }).catch(e => {
                console.error('Copy failed:', e);
            });
        };

        const updateFeedbackNotes = async (id, notes) => {
            try {
                await apiFetch(`/api/feedback/${id}`, {
                    method: 'PATCH',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ agent_notes: notes })
                });
            } catch (e) {
                console.error('Update notes error:', e);
            }
        };

        // ========== SYSTEM OPERATIONS (Aligned with New Frontend) ==========
        const crawlerRunning = ref(false);

        const triggerCrawl = async (force = false) => {
            const msg = force
                ? "⚠️ FORCE REBUILD ALL DATA?\nThis will clear current year cache and re-fetch everything (~5-6 min)."
                : "Trigger analysis? (Background Task)";
            if (!confirm(msg)) return;

            crawlerRunning.value = true;
            try {
                const res = await apiFetch(`/api/admin/crawl?key=secret&force=${force}`, { method: 'POST' });
                const data = await res.json();
                if (res.ok) {
                    alert(`✅ Crawler started!\n${data.message || 'Running in background...'}`);
                } else {
                    alert("❌ Failed: " + (data.detail || "Unknown error"));
                }
            } catch (e) {
                alert("❌ Network Error");
            } finally {
                // Don't reset immediately - let polling check status
                setTimeout(() => { crawlerRunning.value = false; }, 3000);
            }
        };

        const triggerBackup = async () => {
            if (!confirm("Trigger manual backup to GitHub?")) return;
            try {
                const res = await apiFetch('/api/admin/backup', { method: 'POST' });
                const data = await res.json();
                if (res.ok) {
                    alert("✅ Backup Successful!\n" + JSON.stringify(data.details, null, 2));
                } else {
                    alert("❌ Backup Failed: " + (data.detail || "Unknown error"));
                }
            } catch (e) {
                alert("❌ Network Error");
            }
        };

        const triggerPrewarmRefresh = async () => {
            if (!confirm("📦 Rebuild & Push Pre-warm Data to GitHub?\n\nThis will:\n1. Rebuild All (Cold Run) ~5-6 min\n2. Push ~60 cache files to GitHub")) return;
            try {
                crawlerRunning.value = true;
                const res = await apiFetch('/api/admin/refresh-prewarm', { method: 'POST' });
                const data = await res.json();
                if (res.ok) {
                    alert(`✅ Pre-warm Complete!\n${data.message}\n\nDetails: ${JSON.stringify(data.details, null, 2)}`);
                } else {
                    alert("❌ Failed: " + (data.detail || "Unknown error"));
                }
            } catch (e) {
                alert("❌ Network Error");
            } finally {
                crawlerRunning.value = false;
            }
        };


        // Sorting State
        const sortKey = ref('finalValue');
        const sortDesc = ref(true);

        // Simulation State
        const sim = ref({
            startYear: 2006,
            principal: 1000000,
            contribution: 60000
        });

        // Loading state for background calculations
        const isCalculating = ref(false);

        // Cache calculated wealth paths (keyed by stockId) to avoid recalculating for BCR
        const cachedPaths = ref(new Map());

        const stats = computed(() => ({
            total: rawMarsData.value.length,
            filtered: rawMarsData.value.filter(s => s.valid_years > 5).length
        }));

        // Group Stats for Dashboard
        const groupStats = computed(() => {
            const targets = groupTargets.value;
            const marketValue = targets.reduce((sum, t) => sum + (t.summary?.market_value || 0), 0);
            const totalCost = targets.reduce((sum, t) => sum + (t.summary?.total_cost || 0), 0);
            const realized = targets.reduce((sum, t) => sum + (t.summary?.realized_pnl || 0), 0);
            const unrealized = targets.reduce((sum, t) => sum + (t.summary?.unrealized_pnl || 0), 0);
            const unrealizedPct = totalCost > 0 ? (unrealized / totalCost) * 100 : 0;
            return { marketValue, totalCost, realized, unrealized, unrealizedPct };
        });

        // Sorting Logic - Top 50 only
        const sortedMarsList = computed(() => {
            return [...marsList.value].sort((a, b) => {
                let valA = a[sortKey.value];
                let valB = b[sortKey.value];

                // Handle numbers
                if (typeof valA === 'string' && !valA.includes('%')) valA = parseFloat(valA) || valA;
                if (typeof valB === 'string' && !valB.includes('%')) valB = parseFloat(valB) || valB;

                if (valA < valB) return sortDesc.value ? 1 : -1; if (valA > valB) return sortDesc.value ? -1 : 1;
                return 0;
            }).slice(0, 50); // Top 50 only
        });

        const sortBy = (key) => {
            if (sortKey.value === key) {
                sortDesc.value = !sortDesc.value;
            } else {
                sortKey.value = key;
                sortDesc.value = true; // Default to descending for new metrics
            }
        };

        const getSortIcon = (key) => {
            if (sortKey.value !== key) return 'opacity-30';
            return sortDesc.value ? 'text-cyber-cyan' : 'text-cyber-cyan rotate-180 inline-block';
        };

        const formatCurrency = (val) => {
            return new Intl.NumberFormat('en-US', {
                style: 'currency', currency: 'USD', maximumFractionDigits: 0
            }).format(val);
        };

        // Logic: Calculate Wealth Path & Cost Path
        // Logic: Calculate Wealth Path & Cost Path
        const calculateWealthPath = (stockId, startYear, principal, annualContrib) => {
            // DEPRECATED: Logic moved to Backend (/api/race-data)
            // This function is kept only if strictly needed by legacy calls, but returns empty.
            return [];
        };

        // Deprecated simple recalculate, replaced above
        // kept for matching replace if needed, but we replaced fetchMars logic to include recalculate calls
        const old_recalculate = () => { };

        // ========== EXPORT TO CSV ==========
        // ========== EXPORT TO EXCEL ==========
        const exportToExcel = () => {
            const mode = isPremium.value ? 'filtered' : 'raw';
            // Trigger Backend Download with Dynamic Params
            const params = new URLSearchParams({
                mode: mode,
                start_year: sim.value.startYear,
                principal: sim.value.principal,
                contribution: sim.value.contribution
            });
            const url = `/api/export/excel?${params.toString()}`;
            window.location.href = url;
            addNotification('📥 Generating Dynamic Excel (' + mode + ')...');
        };

        const fetchMars = async (year) => {
            try {
                // Default to 2006 if not provided
                const queryYear = year || sim.value.startYear || 2006;
                // Pass full simulation params (Principal, Contribution) to Backend
                const params = new URLSearchParams({
                    start_year: queryYear,
                    principal: sim.value.principal,
                    contribution: sim.value.contribution
                });
                const [res1, res2] = await Promise.all([
                    apiFetch('/api/results'),
                    apiFetch(`/api/race-data?${params.toString()}`)
                ]);
                if (res1.ok) rawMarsData.value = await res1.json();
                if (res2.ok) rawRaceData.value = await res2.json();

                // Trigger local recalculate logic (wealth path lines, sorting)
                // We pass 'false' to avoid infinite recursion if recalculate called fetchMars (it won't, but safety)
                processRecalculation();
            } catch (e) { console.error(e); }
        };

        // Separate local processing from fetching
        const processRecalculation = () => {
            if (!rawRaceData.value.length) return;
            isCalculating.value = true;
            raceRendered.value = false;
            setTimeout(() => {
                // 1. Group Flattened Backend Data by Stock ID
                const groupedData = {};
                rawRaceData.value.forEach(record => {
                    const id = String(record.id);
                    if (!groupedData[id]) groupedData[id] = [];

                    // Transform backend record to frontend path format
                    groupedData[id].push({
                        year: record.year,
                        value: record.wealth || record.value, // Backend provides 'wealth'
                        cost: 0,
                        roi: record.roi,
                        cagr: record.cagr || 0,  // Backend provides per-year CAGR
                        dividend: 0,
                        id: id,
                        name: record.name
                    });
                });

                const pathCache = new Map();
                const simulatedList = rawMarsData.value.map(stock => {
                    const stockId = String(stock.id);

                    // 2. Retrieve Path from Backend Data (Single Source of Truth)
                    // Sort by year just in case
                    const path = (groupedData[stockId] || []).sort((a, b) => a.year - b.year);

                    pathCache.set(stockId, path);

                    if (!path.length) return { ...stock, finalValue: 0, wealthPath: [], totalROI: 0 };

                    const final = path[path.length - 1].value;
                    // Calculate Total ROI based on Principal (Sim Params)
                    // Local calc: 
                    const years = path.length;
                    const totalCost = sim.value.principal + (sim.value.contribution * years);
                    const totalROI = totalCost > 0 ? ((final - totalCost) / totalCost * 100).toFixed(1) : 0;

                    // CAGR
                    let cagr = 0;
                    if (sim.value.principal > 0 && final > 0) {
                        cagr = (Math.pow(final / sim.value.principal, 1 / years) - 1) * 100;
                    }

                    return {
                        ...stock,
                        finalValue: final,
                        wealthPath: path,
                        totalROI: totalROI,
                        cagr: cagr
                    };
                });

                cachedPaths.value = pathCache;
                marsList.value = simulatedList;
                isCalculating.value = false;
                setTimeout(renderRaceChart, 50);
            }, 10);
        };


        const recalculate = () => {
            // Recalculate now implies Fetching Data from Backend to ensure Synchronization
            fetchMars(sim.value.startYear);
        };

        const animationFrames = ref([]); // Store frame data for playback
        const raceRendered = ref(false); // Track if race chart has been rendered

        const raceMetric = ref('wealth'); // Default: Wealth

        // D3.js Bar Chart Race Configuration - RESPONSIVE
        const isMobileRace = () => window.innerWidth < 768;
        const getRaceConfig = () => {
            const mobile = isMobileRace();
            return {
                barHeight: mobile ? 18 : 22,
                barPadding: mobile ? 1 : 2,
                topN: mobile ? 20 : 50, // Show fewer on mobile to fit screen
                duration: 1200, // Slower animation (user request)
                margin: mobile
                    ? { top: 40, right: 80, bottom: 20, left: 100 }  // Compact for mobile
                    : { top: 60, right: 150, bottom: 20, left: 200 } // Spacious for desktop
            };
        };
        // Keep raceConfig as a getter for backward compatibility
        const raceConfig = getRaceConfig();

        // Dynamic Race Chart (D3.js with smooth transitions)
        const renderRaceChart = () => {
            console.log('[D3 Race] renderRaceChart called. rawMarsData:', rawMarsData.value.length);
            if (!rawMarsData.value.length) {
                console.log('[D3 Race] No rawMarsData, returning');
                return;
            }
            raceRendered.value = false;

            // Get fresh config based on current screen size
            const config = getRaceConfig();
            console.log('[D3 Race] Config:', config, 'isMobile:', isMobileRace());

            const container = document.getElementById('race-chart-container');
            console.log('[D3 Race] Container:', container);
            if (!container) {
                console.log('[D3 Race] No container found, returning');
                return;
            }

            // Clear previous
            container.innerHTML = '';

            // Build keyframes data from CACHED paths (avoid recalculation)
            const raceMap = new Map();
            // Create name lookup to avoid "Start" placeholder
            const stockNameMap = new Map();
            // Create CAGR lookup from pre-calculated API values (same as Mars table)
            const stockCagrMap = new Map();
            rawMarsData.value.forEach(stock => {
                stockNameMap.set(String(stock.id), stock.name || String(stock.id));
                stockCagrMap.set(String(stock.id), stock.cagr_pct || 0); // Use API's pre-calculated CAGR
            });

            // Use cached paths if available, otherwise calculate (fallback)
            const pathsToUse = cachedPaths.value.size > 0 ? cachedPaths.value : null;

            rawMarsData.value.forEach(stock => {
                const stockId = String(stock.id);
                // Use cached path if available
                const path = pathsToUse ? pathsToUse.get(stockId) : calculateWealthPath(stockId, sim.value.startYear,
                    sim.value.principal, sim.value.contribution);
                if (!path || path.length === 0) {
                    if (stockId === '6669') {
                        console.log('[DEBUG 6669 MISSING] No path found!', { stockId, pathsToUse: pathsToUse?.size, hasPath: !!path, pathLen: path?.length });
                    }
                    return;
                }

                // For CAGR mode, use pre-calculated value from API (same as Mars table)
                const stockCagr = stockCagrMap.get(stockId) || 0;

                // DEBUG: trace first stock's values
                if (stockId === '6669') {
                    console.log('[DEBUG CAGR]', {
                        stockId,
                        raceMetricValue: raceMetric.value,
                        stockCagr,
                        rawCagrPct: stock.cagr_pct,
                        firstPathValue: path[0]?.value
                    });
                }

                path.forEach(p => {
                    if (!raceMap.has(p.year)) raceMap.set(p.year, []);
                    if (p.year >= sim.value.startYear - 1) {
                        // Backend provides pre-calculated per-year CAGR - Single Source of Truth
                        // No frontend calculation needed - same data for Mars Strategy, CSV Export, and Race
                        raceMap.get(p.year).push({
                            id: p.id,
                            name: stockNameMap.get(p.id) || p.id,
                            // Wealth mode: p.value, CAGR mode: p.cagr (both from backend)
                            value: raceMetric.value === 'wealth' ? p.value : p.cagr
                        });
                    }
                });
            });

            const years = Array.from(raceMap.keys()).filter(y => raceMap.get(y).length > 0).sort((a, b) => a - b);

            // Build keyframes: each frame = { year, data: [ { id, name, value, rank } ] }
            const keyframes = years.map(year => {
                const sorted = raceMap.get(year).sort((a, b) => b.value - a.value).slice(0, config.topN);
                sorted.forEach((d, i) => d.rank = i);
                return { year, data: sorted };
            });

            if (!keyframes.length) {
                console.log('[D3 Race] No keyframes generated, returning');
                return;
            }

            console.log('[D3 Race] Keyframes generated:', keyframes.length, 'years:', years);
            animationFrames.value = keyframes;

            // SVG Setup
            const width = container.clientWidth || 800; // Fallback if hidden
            const height = config.topN * (config.barHeight + config.barPadding) + config.margin.top
                + config.margin.bottom;

            console.log('[D3 Race] Container dimensions:', width, 'x', height, 'd3 defined:', typeof d3);

            const svg = d3.select(container)
                .append('svg')
                .attr('width', width)
                .attr('height', height)
                .attr('viewBox', `0 0 ${width} ${height}`)
                .style('background', 'transparent')
                .style('overflow', 'hidden');  // Prevent bars from overflowing

            console.log('[D3 Race] SVG created:', svg.node());

            // Scales
            const xScale = d3.scaleLinear().range([config.margin.left, width - config.margin.right]);
            const yScale = d3.scaleLinear().range([config.margin.top, height - config.margin.bottom -
                config.barHeight]);
            const colorScale = d3.scaleOrdinal(d3.schemeTableau10);

            // X-Axis
            const xAxis = svg.append('g')
                .attr('class', 'x-axis')
                .attr('transform', `translate(0, ${config.margin.top - 10})`);

            // Year Label (big watermark)
            const yearLabel = svg.append('text')
                .attr('class', 'year-label')
                .attr('x', width - 50)
                .attr('y', height - 30)
                .attr('text-anchor', 'end')
                .attr('fill', 'rgba(255,255,255,0.15)')
                .attr('font-size', isMobileRace() ? '60px' : '100px')
                .attr('font-weight', '900')
                .attr('font-family', 'Inter, sans-serif');

            // Bar Group
            const barsGroup = svg.append('g').attr('class', 'bars');
            const labelsGroup = svg.append('g').attr('class', 'labels');
            const valuesGroup = svg.append('g').attr('class', 'values');

            // Update function for each frame
            window.updateRaceFrame = (frameData, instant = false) => {
                const dur = instant ? 0 : config.duration;
                const data = frameData.data;
                const maxValue = d3.max(data, d => d.value) || 1;

                xScale.domain([0, maxValue * 1.1]);
                yScale.domain([0, config.topN - 1]);

                // DEBUG: Log bar width calculation
                if (data.length > 0) {
                    const sample = data[0];
                    console.log('[Bar Width Debug]', {
                        year: frameData.year,
                        sampleValue: sample.value,
                        maxValue,
                        marginLeft: raceConfig.margin.left,
                        xScaleRange: xScale.range(),
                        calculatedWidth: xScale(sample.value) - raceConfig.margin.left
                    });
                }

                // X-Axis transition
                xAxis.transition().duration(dur).call(d3.axisTop(xScale).ticks(5).tickFormat(d => raceMetric.value ===
                    'wealth' ? formatCurrency(d) : `${d.toFixed(0)}%`));
                xAxis.selectAll('text').attr('fill', '#888');
                xAxis.selectAll('line, path').attr('stroke', '#333');

                // Year watermark
                yearLabel.text(frameData.year);

                // BARS with key-based join for object constancy
                const bars = barsGroup.selectAll('rect').data(data, d => d.id);

                // EXIT: Simple fade out
                bars.exit()
                    .transition()
                    .duration(dur)
                    .attr('width', 0)
                    .remove();

                // ENTER + UPDATE: Smooth transitions
                bars.enter()
                    .append('rect')
                    .attr('x', config.margin.left)
                    .attr('y', d => yScale(d.rank))
                    .attr('height', config.barHeight)
                    .attr('fill', d => colorScale(d.id))
                    .attr('rx', 4)
                    .attr('width', 0)
                    .merge(bars)
                    .transition()
                    .duration(dur)
                    .ease(d3.easeCubicInOut)  // Smooth cubic easing
                    .attr('y', d => yScale(d.rank))
                    .attr('width', d => Math.max(0, xScale(d.value) - config.margin.left));

                // LABELS (stock names on left)
                const labels = labelsGroup.selectAll('text').data(data, d => d.id);

                labels.exit().transition().duration(dur).style('opacity', 0).remove();

                labels.enter()
                    .append('text')
                    .attr('x', config.margin.left - 5)
                    .attr('y', d => yScale(d.rank) + config.barHeight / 2)
                    .attr('text-anchor', 'end')
                    .attr('fill', '#fff')
                    .attr('font-size', isMobileRace() ? '9px' : '11px')
                    .attr('dominant-baseline', 'middle')
                    .style('opacity', 0)
                    .merge(labels)
                    .transition()
                    .duration(dur)
                    .ease(d3.easeCubicInOut)
                    .attr('y', d => yScale(d.rank) + config.barHeight / 2)
                    .style('opacity', 1)
                    .text(d => `${d.name} (${d.id})`);

                // VALUES (outside bars on right)
                const values = valuesGroup.selectAll('text').data(data, d => d.id);

                values.exit().transition().duration(dur).style('opacity', 0).remove();

                values.enter()
                    .append('text')
                    .attr('x', d => xScale(d.value) + 8)  // Position OUTSIDE bar (right side)
                    .attr('y', d => yScale(d.rank) + config.barHeight / 2)
                    .attr('text-anchor', 'start')  // Align from left edge of text
                    .attr('fill', '#00ffff')  // Cyber cyan for visibility
                    .attr('font-size', isMobileRace() ? '8px' : '10px')
                    .attr('font-weight', '700')
                    .attr('dominant-baseline', 'middle')
                    .style('opacity', 0)
                    .style('text-shadow', '0 0 3px #000, 0 0 5px #000, 1px 1px 2px #000')  // Dark shadow for contrast
                    .merge(values)
                    .transition()
                    .duration(dur)
                    .ease(d3.easeCubicInOut)
                    .attr('x', d => xScale(d.value) + 8)  // Position OUTSIDE bar
                    .attr('y', d => yScale(d.rank) + config.barHeight / 2)
                    .style('opacity', 1)
                    .text(d => raceMetric.value === 'wealth' ? formatCurrency(d.value) : `${d.value.toFixed(1)}%`);
            };

            // Initial render (first frame)
            console.log('[D3 Race] Calling updateRaceFrame with first keyframe:', keyframes[0]);
            window.updateRaceFrame(keyframes[0], true);
            console.log('[D3 Race] renderRaceChart complete. raceRendered:', true);
            raceRendered.value = true;
        }; // End renderRaceChart

        const isPlaying = ref(false);
        const currentFrameIndex = ref(0);
        let animationInterval = null;

        const pauseRace = () => {
            isPlaying.value = false;
            if (animationInterval) clearInterval(animationInterval);
            animationInterval = null;
        };

        const playRace = () => {
            if (isPlaying.value || !animationFrames.value.length) return;

            isPlaying.value = true;

            // Start D3.js animation loop
            animationInterval = setInterval(() => {
                const nextIndex = currentFrameIndex.value + 1;

                // Stop if end reached
                if (nextIndex >= animationFrames.value.length) {
                    pauseRace();
                    return;
                }

                // Get next keyframe and update D3 chart with smooth transition
                const nextFrame = animationFrames.value[nextIndex];
                if (window.updateRaceFrame) {
                    window.updateRaceFrame(nextFrame, false);
                }

                currentFrameIndex.value = nextIndex;

            }, 1500); // 1500ms interval for slower animation (user request)
        };

        const resetRace = () => {
            pauseRace();
            currentFrameIndex.value = 0;
            // ALWAYS re-render the chart to rebuild keyframes with current raceMetric
            // This is needed because metric switch requires new keyframe values
            renderRaceChart();
        };

        // Timeline scrubber seek function (Flourish-style rollback)
        const seekToFrame = (index) => {
            pauseRace();
            const targetIndex = parseInt(index, 10);
            if (targetIndex >= 0 && targetIndex < animationFrames.value.length) {
                currentFrameIndex.value = targetIndex; if (window.updateRaceFrame) {
                    window.updateRaceFrame(animationFrames.value[targetIndex], false);
                }
            }
        };

        const resultTab = ref('wealth'); // 'wealth' | 'dividend'

        const simulateShareAccumulation = (stockId, history) => {
            let shares = 0;
            let wealth = 0;
            let cost = 0;
            const path = [];
            const principal = sim.value.principal;
            const contribution = sim.value.contribution;

            // Initial Purchase (2006)
            const startData = history.find(h => h.year === sim.value.startYear);
            if (startData && startData.price_start > 0) {
                shares = principal / startData.price_start;
                cost += principal;
                wealth = shares * startData.price_end; // End of Year 1
            }

            // Loop years
            for (let y = sim.value.startYear; y <= 2025; y++) {
                const yearData = history.find(h => h.year === y);
                if (yearData) {
                    const avgPrice = (yearData.price_start + yearData.price_end) / 2;

                    // 1. Receive Dividend
                    const cashDiv = shares * yearData.div_cash;

                    // 2. Reinvest (Buy Shares)
                    // Only if price > 0
                    if (avgPrice > 0) {
                        const sharFromDiv = cashDiv / avgPrice;
                        const shareFromContrib = contribution / avgPrice;
                        shares += (sharFromDiv + shareFromContrib);
                        cost += contribution;
                    }

                    // 3. Update Wealth (End of Year)
                    wealth = shares * yearData.price_end;

                    // Simple ROI
                    const roiPct = cost > 0 ? ((wealth - cost) / cost) * 100 : 0;

                    // CAGR
                    const yearsElapsed = y - sim.value.startYear + 1;
                    let cagr = 0;
                    if (yearsElapsed > 0 && principal > 0) {
                        cagr = (Math.pow(wealth / principal, 1 / yearsElapsed) - 1) * 100;
                    }

                    path.push({
                        year: y,
                        value: wealth,
                        dividend: cashDiv,
                        roi: roiPct,
                        cagr: cagr
                    });
                }
            }
            return path;
        };

        // Detail Chart Renderer - must be defined before openDetail/watch that use it
        const renderDetailChart = (stock) => {
            if (!stock || !stock.wealthPath) return;
            const isWealth = resultTab.value === 'wealth';
            const trace = {
                x: stock.wealthPath.map(d => d.year),
                y: isWealth ? stock.wealthPath.map(d => d.value) : stock.wealthPath.map(d => d.dividend || 0),
                type: 'scatter',
                mode: 'lines+markers',
                name: isWealth ? 'Buy At Opening' : 'Yearly Cash Div.',
                line: { color: isWealth ? '#00f2ea' : '#ff0055', width: 3 },
                fill: 'tozeroy',
                fillcolor: isWealth ? 'rgba(0, 242, 234, 0.1)' : 'rgba(255, 0, 85, 0.1)'
            };

            const layout = {
                title: false,
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(255,255,255,0.05)',
                font: { color: '#aaa' },
                margin: { t: 20, l: 40, r: 20, b: 40 },
                xaxis: { gridcolor: '#333' },
                yaxis: { gridcolor: '#333' }
            };

            Plotly.newPlot('detail-chart', [trace], layout);
        };


        const openDetail = async (stock) => {
            // Use pre-computed data from backend (same as table)
            // stock already has wealthPath and finalValue from processRecalculation
            detailStock.value = stock;
            resultTab.value = 'wealth';

            // If wealthPath is missing, try to build from cachedPaths
            if (!stock.wealthPath || stock.wealthPath.length === 0) {
                const cached = cachedPaths.value.get(String(stock.id));
                if (cached && cached.length > 0) {
                    detailStock.value = {
                        ...stock,
                        wealthPath: cached,
                        finalValue: cached[cached.length - 1].value,
                        totalROI: stock.totalROI || 0,
                        cagr: stock.cagr_pct || stock.cagr || 0
                    };
                }
            }

            nextTick(() => renderDetailChart(detailStock.value));
        };


        // Reactive Chart Update - watch() for tab changes
        watch(resultTab, () => {
            if (detailStock.value) {
                renderDetailChart(detailStock.value);
            }
        });

        // renderDetailChart is now defined above openDetail (line ~1230)

        const analyzeCB = async () => {
            loadingCB.value = true;
            cbResult.value = null;
            try {
                const res = await apiFetch(`/api/cb/analyze?code=${cbInput.value}`);
                const data = await res.json();
                cbResult.value = data;
            } catch (e) { console.error(e); }
            loadingCB.value = false;
        };

        const getActionColor = (action) => {
            if (!action) return 'text-gray-500';
            if (action.includes('BUY')) return 'text-green-400';
            if (action.includes('SELL')) return 'text-red-500';
            return 'text-yellow-400';
        };

        const getBorderColor = (action) => {
            if (!action) return 'border-gray-500';
            if (action.includes('BUY')) return 'border-green-400 from-green-500/10';
            if (action.includes('SELL')) return 'border-red-500 from-red-500/10';
            return 'border-yellow-400 from-yellow-500/10';
        };

        // ============== PORTFOLIO STATE ==============
        const portfolioGroups = ref([]);
        const selectedGroupId = ref(null);
        const groupTargets = ref([]);
        const showAddGroup = ref(false);
        const newGroupName = ref('');
        const newTargetId = ref('');
        const newTargetName = ref('');
        const showTxForm = ref(null);
        const newTx = ref({
            type: 'buy', shares: 0, price: 0, date: new Date().toISOString().split('T')[0]
        });

        // Dividend tracking
        const dividendCash = ref({ total_cash: 0, dividend_count: 0 });
        const syncingDividends = ref(false);

        // Fetch dividend cash
        const fetchDividendCash = async () => {
            try {
                const res = await apiFetch('/api/portfolio/cash');
                dividendCash.value = await res.json();
            } catch (e) { console.error('Fetch dividend cash error:', e); }
        };

        // Sync dividends
        const syncDividends = async () => {
            syncingDividends.value = true;
            try {
                const res = await apiFetch('/api/portfolio/sync-dividends', { method: 'POST' });
                const result = await res.json();
                console.log('Synced dividends:', result);
                await fetchDividendCash();
                alert('Synced ' + (result.synced_count || 0) + ' new dividends!');
            } catch (e) { console.error('Sync dividends error:', e); }
            syncingDividends.value = false;
        };

        // Fetch all groups
        const fetchGroups = async () => {
            // GUEST MODE: Load from localStorage
            if (isGuest.value) {
                portfolioGroups.value = guestData.value.groups.map(g => ({
                    id: g.id,
                    name: g.name,
                    targets: g.targets || []
                }));
                if (portfolioGroups.value.length && !selectedGroupId.value) {
                    selectGroup(portfolioGroups.value[0].id);
                }
                return;
            }
            // LOGGED IN: Use API
            try {
                const res = await apiFetch('/api/portfolio/groups');
                portfolioGroups.value = await res.json();
                if (portfolioGroups.value.length && !selectedGroupId.value) {
                    selectGroup(portfolioGroups.value[0].id);
                }
            } catch (e) { console.error('Fetch groups error:', e); }
        };

        // Create group
        const createGroup = async () => {
            if (!newGroupName.value.trim()) return;

            // GUEST MODE: Save to localStorage
            if (isGuest.value) {
                if (guestData.value.groups.length >= GUEST_LIMITS.maxGroups) {
                    alert(`⚠️ Guest limit reached!\n\nMax ${GUEST_LIMITS.maxGroups} groups allowed.\nLogin to create more groups.`);
                    return;
                }
                const newGroup = {
                    id: guestData.value.nextGroupId++,
                    name: newGroupName.value.trim(),
                    targets: []
                };
                guestData.value.groups.push(newGroup);
                saveGuestData(guestData.value);
                newGroupName.value = '';
                showAddGroup.value = false;
                await fetchGroups();
                addNotification(`✅ Group "${newGroup.name}" created (local)`);
                return;
            }

            // LOGGED IN: Use API
            try {
                const res = await apiFetch('/api/portfolio/groups', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: newGroupName.value.trim() })
                });
                if (res.ok) {
                    newGroupName.value = '';
                    showAddGroup.value = false;
                    await fetchGroups();
                } else {
                    const err = await res.json();
                    alert(err.error || 'Create failed');
                }
            } catch (e) { console.error('Create group error:', e); }
        };

        // Delete group
        const deleteGroup = async (groupId) => {
            if (!confirm('Delete this group and all targets?')) return;

            // GUEST MODE: Delete from localStorage
            if (isGuest.value) {
                guestData.value.groups = guestData.value.groups.filter(g => g.id !== groupId);
                saveGuestData(guestData.value);
                if (selectedGroupId.value === groupId) {
                    selectedGroupId.value = null;
                    groupTargets.value = [];
                }
                await fetchGroups();
                addNotification('🗑️ Group deleted (local)');
                return;
            }

            // LOGGED IN: Use API
            try {
                await apiFetch(`/api/portfolio/groups/${groupId}`, { method: 'DELETE' });
                if (selectedGroupId.value === groupId) {
                    selectedGroupId.value = null;
                    groupTargets.value = [];
                }
                await fetchGroups();
            } catch (e) { console.error('Delete group error:', e); }
        };

        // Select group and load targets
        // Select group and load targets with live prices
        const selectGroup = async (groupId) => {
            selectedGroupId.value = groupId;

            // GUEST MODE: Load from localStorage
            if (isGuest.value) {
                const group = guestData.value.groups.find(g => g.id === groupId);
                if (group) {
                    groupTargets.value = (group.targets || []).map(t => ({
                        ...t,
                        livePrice: { price: 0, change: 0, change_pct: 0 },
                        summary: {
                            total_shares: t.transactions?.reduce((sum, tx) => sum + (tx.type === 'buy' ? tx.shares : -tx.shares), 0) || 0,
                            avg_cost: t.transactions?.length > 0 ? t.transactions.reduce((sum, tx) => sum + tx.price * tx.shares, 0) / t.transactions.reduce((sum, tx) => sum + tx.shares, 0) : 0,
                            realized_pl: 0,
                            unrealized_pl: 0
                        }
                    }));
                }
                return;
            }

            // LOGGED IN: Use API
            try {
                const res = await apiFetch(`/api/portfolio/groups/${groupId}/targets`);
                const targets = await res.json();

                const stockIds = targets.map(t => t.stock_id).join(',');
                let livePrices = {};
                if (stockIds) {
                    try {
                        const priceRes = await apiFetch(`/api/portfolio/prices?stock_ids=${stockIds}`);
                        livePrices = await priceRes.json();
                    } catch (e) { console.warn('Live price fetch failed:', e); }
                }

                for (const t of targets) {
                    const livePrice = livePrices[t.stock_id]?.price || null;
                    t.livePrice = livePrices[t.stock_id] || { price: 0, change: 0, change_pct: 0 };

                    const sumUrl = livePrice
                        ? `/api/portfolio/targets/${t.id}/summary?current_price=${livePrice}`
                        : `/api/portfolio/targets/${t.id}/summary`;
                    const sumRes = await apiFetch(sumUrl);
                    t.summary = await sumRes.json();
                }
                groupTargets.value = targets;
            } catch (e) { console.error('Load targets error:', e); }
        };

        // Add target
        const addTarget = async () => {
            if (!newTargetId.value.trim() || !selectedGroupId.value) return;

            // GUEST MODE: Save to localStorage
            if (isGuest.value) {
                const group = guestData.value.groups.find(g => g.id === selectedGroupId.value);
                if (!group) return;

                if ((group.targets || []).length >= GUEST_LIMITS.maxTargetsPerGroup) {
                    alert(`⚠️ Guest limit reached!\n\nMax ${GUEST_LIMITS.maxTargetsPerGroup} targets per group.\nLogin to add more targets.`);
                    return;
                }

                let finalName = newTargetName.value.trim();
                if (!finalName && marsList.value.length) {
                    const found = marsList.value.find(s => s.id === newTargetId.value.trim());
                    if (found) finalName = found.name;
                }

                const newTarget = {
                    id: guestData.value.nextTargetId++,
                    stock_id: newTargetId.value.trim(),
                    stock_name: finalName || newTargetId.value.trim(),
                    transactions: []
                };
                if (!group.targets) group.targets = [];
                group.targets.push(newTarget);
                saveGuestData(guestData.value);
                newTargetId.value = '';
                newTargetName.value = '';
                await selectGroup(selectedGroupId.value);
                addNotification(`✅ ${newTarget.stock_name} added (local)`);
                return;
            }

            // LOGGED IN: Use API
            try {
                let finalName = newTargetName.value.trim();
                if (!finalName && marsList.value.length) {
                    const found = marsList.value.find(s => s.id === newTargetId.value.trim());
                    if (found) finalName = found.name;
                }

                const res = await apiFetch(`/api/portfolio/groups/${selectedGroupId.value}/targets`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ stock_id: newTargetId.value.trim(), stock_name: finalName || null })
                });
                if (res.ok) {
                    const data = await res.json(); // Get the created target
                    newTargetId.value = '';
                    newTargetName.value = '';
                    await selectGroup(selectedGroupId.value);

                    // Show success with actual name
                    const nameToShow = data.stock_name || data.stock_id;
                    addNotification(`✅ ${nameToShow} added`);
                } else {
                    const err = await res.json();
                    alert(err.error || 'Add target failed');
                }
            } catch (e) { console.error('Add target error:', e); }
        };

        // Delete target
        const deleteTarget = async (targetId) => {
            if (!confirm('Delete this stock and all transactions?')) return;

            // GUEST MODE: Delete from localStorage
            if (isGuest.value) {
                const group = guestData.value.groups.find(g => g.id === selectedGroupId.value);
                if (group) {
                    group.targets = (group.targets || []).filter(t => t.id !== targetId);
                    saveGuestData(guestData.value);
                    await selectGroup(selectedGroupId.value);
                    addNotification('🗑️ Target deleted (local)');
                }
                return;
            }

            // LOGGED IN: Use API
            try {
                await apiFetch(`/api/portfolio/targets/${targetId}`, { method: 'DELETE' });
                await selectGroup(selectedGroupId.value);
            } catch (e) { console.error('Delete target error:', e); }
        };

        // Add or Update transaction
        const addTransaction = async () => {
            if (!showTxForm.value || !newTx.value.shares || !newTx.value.price) return;

            // GUEST MODE: Save to localStorage
            if (isGuest.value) {
                const group = guestData.value.groups.find(g => g.id === selectedGroupId.value);
                if (!group) return;
                const target = (group.targets || []).find(t => t.id === showTxForm.value);
                if (!target) return;

                if (!target.transactions) target.transactions = [];

                const isEdit = !!newTx.value.id;
                if (isEdit) {
                    // Update existing
                    const idx = target.transactions.findIndex(tx => tx.id === newTx.value.id);
                    if (idx >= 0) target.transactions[idx] = { ...newTx.value };
                } else {
                    // Add new
                    if (target.transactions.length >= GUEST_LIMITS.maxTransactionsPerTarget) {
                        alert(`⚠️ Guest limit reached!\n\nMax ${GUEST_LIMITS.maxTransactionsPerTarget} transactions per target.\nLogin to add more transactions.`);
                        return;
                    }
                    target.transactions.push({
                        id: guestData.value.nextTxId++,
                        ...newTx.value
                    });
                }
                saveGuestData(guestData.value);
                showTxForm.value = null;
                newTx.value = { type: 'buy', shares: 0, price: 0, date: new Date().toISOString().split('T')[0] };
                await selectGroup(selectedGroupId.value);
                addNotification('✅ Transaction saved (local)');
                return;
            }

            // LOGGED IN: Use API
            const isEdit = !!newTx.value.id;
            const url = isEdit
                ? `/api/portfolio/transactions/${newTx.value.id}`
                : `/api/portfolio/targets/${showTxForm.value}/transactions`;
            const method = isEdit ? 'PUT' : 'POST';

            try {
                const res = await apiFetch(url, {
                    method: method,
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(newTx.value)
                });
                if (res.ok) {
                    showTxForm.value = null;
                    newTx.value = { type: 'buy', shares: 0, price: 0, date: new Date().toISOString().split('T')[0] };
                    await selectGroup(selectedGroupId.value);

                    // If history is open, refresh it
                    if (showTxHistory.value) await fetchTxHistory(showTxHistory.value);

                    // Refresh dependent data for other tabs
                    fetchTrendData();
                    fetchPortfolioRaceData();
                    fetchLeaderboard();
                } else {
                    const err = await res.json();
                    alert(err.error || 'Transaction failed');
                }
            } catch (e) { console.error('Transaction error:', e); }
        };

        // Transaction History
        const showTxHistory = ref(null); // target_id
        const txHistory = ref([]);

        const fetchTxHistory = async (targetId) => {
            try {
                const res = await apiFetch(`/api/portfolio/targets/${targetId}/transactions`);
                txHistory.value = await res.json();
            } catch (e) { console.error('Fetch history error:', e); }
        };

        const openHistory = async (target) => {
            showTxHistory.value = target.id;
            await fetchTxHistory(target.id);
        };

        const deleteTx = async (txId) => {
            if (!confirm('Start deletion sequence?')) return;
            try {
                await apiFetch(`/api/portfolio/transactions/${txId}`, { method: 'DELETE' });
                await fetchTxHistory(showTxHistory.value);
                await selectGroup(selectedGroupId.value);
            } catch (e) { console.error('Delete tx error:', e); }
        };

        const openEditTx = (tx) => {
            // Close history temporarily or keep it open?
            // Let's close history to show form, or show form on top.
            // For simplicity, just set form data.
            if (!showTxHistory.value) return;

            // We need target_id for the form context
            showTxForm.value = showTxHistory.value;
            newTx.value = { ...tx }; // Copy data
        };

        // ============== TREND DASHBOARD STATE ==============
        const trendData = ref([]);
        const assetGroups = ref({ stock: [], etf: [], cb: [] });
        const expandedGroup = ref(null);
        const selectedMonth = ref(null);
        const portfolioRaceData = ref([]);
        const portfolioRacePlaying = ref(false);
        const trendLivePrices = ref({});

        // Computed: max trend cost for chart scaling
        const maxTrendCost = computed(() => {
            const costs = trendData.value.map(t => t.cost);
            return Math.max(1, ...costs);
        });

        // Fetch trend data
        const fetchTrendData = async () => {
            try {
                // Fetch ALL trend history (months=0 means get all data from first transaction)
                const trendRes = await apiFetch('/api/portfolio/trend?months=0');
                trendData.value = await trendRes.json();
                if (trendData.value.length) {
                    selectedMonth.value = trendData.value[trendData.value.length - 1]?.month;
                }

                // Render Plotly chart with zoom
                renderTrendChart();

                // Fetch asset groups
                const groupRes = await apiFetch('/api/portfolio/by-type');
                const groups = await groupRes.json();
                assetGroups.value = groups;

                // Collect all stock IDs to fetch current prices
                const allTargets = [...(groups.stock || []), ...(groups.etf || []), ...(groups.cb || [])];
                const ids = allTargets.map(t => t.stock_id).filter(id => id).join(',');

                if (ids) {
                    const priceRes = await apiFetch(`/api/portfolio/prices?stock_ids=${ids}`);
                    trendLivePrices.value = await priceRes.json();
                }

                // Fetch race data
                const raceRes = await apiFetch('/api/portfolio/race-data');
                portfolioRaceData.value = await raceRes.json();
            } catch (e) { console.error('Fetch trend error:', e); }
        };

        // Render trend chart with Plotly (supports zoom/pan)
        const renderTrendChart = () => {
            const container = document.getElementById('trend-chart-container');
            if (!container || !trendData.value.length) return;

            const months = trendData.value.map(t => t.month);
            const costs = trendData.value.map(t => t.cost);

            const trace = {
                x: months,
                y: costs,
                type: 'scatter',
                mode: 'lines',
                fill: 'tozeroy',
                fillcolor: 'rgba(0, 242, 234, 0.3)',
                line: {
                    color: '#00f2ea',
                    width: 3,
                    shape: 'spline',
                    smoothing: 1.3
                },
                hovertemplate: '%{x}<br>Cost: $%{y:,.0f}<extra></extra>'
            };

            const layout = {
                paper_bgcolor: 'transparent',
                plot_bgcolor: 'transparent',
                margin: { l: 60, r: 20, t: 20, b: 60 },
                xaxis: {
                    type: 'category',
                    tickangle: -45,
                    tickfont: { color: '#888', size: 10 },
                    gridcolor: 'rgba(255,255,255,0.05)'
                },
                yaxis: {
                    tickformat: '$,.0f',
                    tickfont: { color: '#888', size: 10 },
                    gridcolor: 'rgba(255,255,255,0.1)'
                },
                dragmode: 'zoom',
                hovermode: 'closest'
            };

            const config = {
                responsive: true,
                displayModeBar: true,
                modeBarButtonsToInclude: ['zoom2d', 'pan2d', 'resetScale2d', 'toImage'],
                displaylogo: false
            };

            Plotly.newPlot(container, [trace], layout, config);

            // Handle click on data point to select month
            container.on('plotly_click', (data) => {
                if (data.points && data.points[0]) {
                    selectedMonth.value = data.points[0].x;
                }
            });
        };


        // Get group total (Calculated with live prices)
        const getGroupTotal = (type) => {
            const targets = assetGroups.value[type] || [];
            let total = 0;
            for (const t of targets) {
                const price = trendLivePrices.value[t.stock_id]?.price || 0;
                total += (t.total_shares || 0) * price;
            }
            return total;
        };

        // Portfolio race controls
        const playPortfolioRace = () => {
            portfolioRacePlaying.value = true;
            console.log('Portfolio race started with', portfolioRaceData.value.length, 'data points');
        };

        const pausePortfolioRace = () => {
            portfolioRacePlaying.value = false;
        };

        // Fetch portfolio race data
        const fetchPortfolioRaceData = async () => {
            try {
                const raceRes = await apiFetch('/api/portfolio/race-data');
                portfolioRaceData.value = await raceRes.json();

                // Also fetch asset groups for stats
                const groupRes = await apiFetch('/api/portfolio/by-type');
                assetGroups.value = await groupRes.json();
            } catch (e) { console.error('Fetch race data error:', e); }
        };

        // Portfolio Race Animation Variables
        let portfolioRaceInterval = null;
        let portfolioRaceFrameIndex = 0;

        // Render Portfolio Race using D3 (simplified bar chart race)
        const renderPortfolioRace = () => {
            const container = document.getElementById('my-portfolio-race-chart');
            if (!container || portfolioRaceData.value.length === 0) return;

            // Clear existing content
            container.innerHTML = '';

            // Group data by month
            const monthMap = new Map();
            portfolioRaceData.value.forEach(d => {
                if (!monthMap.has(d.month)) monthMap.set(d.month, []);
                monthMap.get(d.month).push(d);
            });
            const months = Array.from(monthMap.keys()).sort();
            if (months.length === 0) return;

            // Setup D3
            const width = container.clientWidth || 600;
            const height = container.clientHeight || 400;
            const margin = { top: 40, right: 100, bottom: 30, left: 120 };
            const n = 10; // Max bars to show

            const svg = d3.select(container)
                .append('svg')
                .attr('width', width)
                .attr('height', height)
                .style('background', 'transparent');

            const x = d3.scaleLinear().range([margin.left, width - margin.right]);
            const y = d3.scaleBand().range([margin.top, height - margin.bottom]).padding(0.1);

            const gBars = svg.append('g');
            const gLabels = svg.append('g');
            const gValues = svg.append('g');
            const gMonth = svg.append('text')
                .attr('x', width - margin.right - 10)
                .attr('y', height - 10)
                .attr('text-anchor', 'end')
                .attr('font-size', '24px')
                .attr('fill', '#00f2ea')
                .attr('font-weight', 'bold');

            const colors = ['#00f2ea', '#ff6b6b', '#ffd93d', '#6bcb77', '#4d96ff', '#ff922b'];

            const updateFrame = (monthData, monthLabel) => {
                const topN = monthData.sort((a, b) => b.value - a.value).slice(0, n);

                x.domain([0, d3.max(topN, d => d.value) || 100]);
                y.domain(topN.map(d => d.id));

                // Bars
                const bars = gBars.selectAll('rect').data(topN, d => d.id);
                bars.join(
                    enter => enter.append('rect')
                        .attr('x', margin.left)
                        .attr('y', d => y(d.id))
                        .attr('height', y.bandwidth())
                        .attr('width', 0)
                        .attr('fill', (d, i) => colors[i % colors.length])
                        .attr('rx', 4)
                        .call(e => e.transition().duration(300).attr('width', d => x(d.value) - margin.left)),
                    update => update.call(u => u.transition().duration(300)
                        .attr('y', d => y(d.id))
                        .attr('width', d => x(d.value) - margin.left)),
                    exit => exit.remove()
                );

                // Labels (stock names)
                const labels = gLabels.selectAll('text').data(topN, d => d.id);
                labels.join(
                    enter => enter.append('text')
                        .attr('x', margin.left - 5)
                        .attr('y', d => y(d.id) + y.bandwidth() / 2)
                        .attr('dy', '0.35em')
                        .attr('text-anchor', 'end')
                        .attr('fill', '#fff')
                        .attr('font-size', '12px')
                        .text(d => d.name?.substring(0, 8) || d.id),
                    update => update.call(u => u.transition().duration(300)
                        .attr('y', d => y(d.id) + y.bandwidth() / 2)
                        .text(d => d.name?.substring(0, 8) || d.id)),
                    exit => exit.remove()
                );

                // Values
                const values = gValues.selectAll('text').data(topN, d => d.id);
                values.join(
                    enter => enter.append('text')
                        .attr('x', d => x(d.value) + 5)
                        .attr('y', d => y(d.id) + y.bandwidth() / 2)
                        .attr('dy', '0.35em')
                        .attr('fill', '#fff')
                        .attr('font-size', '11px')
                        .text(d => '$' + d.value.toLocaleString()),
                    update => update.call(u => u.transition().duration(300)
                        .attr('x', d => x(d.value) + 5)
                        .attr('y', d => y(d.id) + y.bandwidth() / 2)
                        .text(d => '$' + d.value.toLocaleString())),
                    exit => exit.remove()
                );

                // Month label
                gMonth.text(monthLabel);
            };

            // Animation loop
            portfolioRaceFrameIndex = 0;
            const animate = () => {
                if (!portfolioRacePlaying.value) return;
                if (portfolioRaceFrameIndex >= months.length) {
                    portfolioRacePlaying.value = false;
                    return;
                }
                const month = months[portfolioRaceFrameIndex];
                updateFrame(monthMap.get(month), month);
                portfolioRaceFrameIndex++;
            };

            // Initial frame
            updateFrame(monthMap.get(months[0]), months[0]);

            // Start animation
            if (portfolioRaceInterval) clearInterval(portfolioRaceInterval);
            portfolioRaceInterval = setInterval(animate, 600);
        };

        // Watch for play state and trigger render
        watch(portfolioRacePlaying, (playing) => {
            if (playing) {
                renderPortfolioRace();
            } else if (portfolioRaceInterval) {
                clearInterval(portfolioRaceInterval);
            }
        });

        // ============== LEADERBOARD & PROFILE ==============
        const leaderboard = ref([]);
        // currentUser, showSettings, etc are global refs declared at top
        const loadingLadder = ref(false);
        const newNickname = ref('');
        const showProfileModal = ref(false);
        const profileData = ref(null);
        const mobileMenuOpen = ref(false); // Mobile Nav State

        // Dividend Modal State
        const showDivDetails = ref(null);

        const currentYear = new Date().getFullYear();

        const fetchLeaderboard = async () => {
            loadingLadder.value = true;
            try {
                const res = await apiFetch('/api/leaderboard');
                leaderboard.value = await res.json();
            } catch (e) { console.error('Leaderboard error:', e); }
            loadingLadder.value = false;
        };

        const openProfile = async (userId) => {
            try {
                const res = await apiFetch(`/api/public/profile/${userId}`);
                if (res.ok) {
                    profileData.value = await res.json();
                    showProfileModal.value = true;
                }
            } catch (e) { console.error('Profile fetch error:', e); }
        };

        const getDonutGradient = (allocation) => {
            if (!allocation || !allocation.length) return 'gray 0% 100%';
            let gradient = [];
            let current = 0;
            const colors = ['#00e5ff', '#ff2d55', '#ffcc00', '#aa00ff']; // Cyan, Pink, Gold, Purple
            allocation.forEach((item, idx) => {
                const next = current + item.pct;
                gradient.push(`${colors[idx % colors.length]} ${current}% ${next}%`);
                current = next;
            });
            return gradient.join(', ');
        };

        const syncStats = async () => {
            try {
                const res = await apiFetch('/api/portfolio/sync-stats', { method: 'POST' });
                if (res.ok) {
                    const data = await res.json();
                    alert(`Rank Synced! ROI: ${data.roi}%`);
                    fetchLeaderboard(); // Refresh list if open
                } else {
                    alert('Sync failed.');
                }
            } catch (e) { console.error('Sync stats error:', e); }
        };

        const updateProfile = async () => {
            if (!newNickname.value.trim()) return;
            try {
                const res = await apiFetch('/api/auth/profile', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ nickname: newNickname.value.trim() })
                });
                const data = await res.json();
                if (data.status === 'ok') {
                    currentUser.value.nickname = data.nickname;
                    alert('Nickname updated!');
                }
            } catch (e) { alert('Update failed'); }
        };

        const copyPublicLink = () => {
            if (!currentUser.value || !currentUser.value.id) return;
            const link = `${window.location.origin}/?profile=${currentUser.value.id}`;
            navigator.clipboard.writeText(link).then(() => {
                alert('Public Profile Link Copied! 🔗\n' + link);
            });
        };

        onMounted(async () => {
            const loader = document.getElementById('loading-msg');

            // Check for Query Params (Profile Sharing)
            const urlParams = new URLSearchParams(window.location.search);
            const sharedProfileId = urlParams.get('profile');
            if (sharedProfileId) {
                openProfile(sharedProfileId);
            }

            const loadDashboard = () => {
                // Load settings and apply default tab
                loadSettings();
                currentTab.value = appSettings.value.defaultTab || 'mars';

                fetchMars();
                fetchGroups(); // Load portfolio on startup
                fetchDividendCash(); // Load dividend cash
                startNotifPolling(); // Start Premium Alert Polling

                watch(currentTab, (newTab) => {
                    if (newTab === 'race') {
                        if (raceRendered.value) {
                            setTimeout(() => Plotly.Plots.resize('race-chart-container'), 50);
                        } else {
                            setTimeout(renderRaceChart, 100);
                        }
                    } else if (newTab === 'portfolio') {
                        fetchGroups();
                    } else if (newTab === 'trend') {
                        fetchTrendData();
                    } else if (newTab === 'myrace') {
                        fetchPortfolioRaceData();
                    } else if (newTab === 'cb') {
                        fetchPortfolioCBs();
                    } else if (newTab === 'ladder') {
                        fetchLeaderboard();
                    } else if (newTab === 'admin') {
                        fetchAdminMetrics();
                        fetchFeedbackList();
                    }
                });
            };

            // Check Auth
            try {
                const res = await apiFetch('/auth/me');
                const user = await res.json();
                if (user && user.id) {
                    currentUser.value = user;
                    newNickname.value = user.nickname || '';
                    loadDashboard();
                    // Hide loader after dashboard init
                    if (loader) loader.style.display = 'none';
                } else {
                    // User not logged in, show Overlay
                    if (loader) loader.style.display = 'none';
                }
            } catch (e) {
                console.error('Auth Error', e);
                if (loader) loader.style.display = 'none';
            }

            // Watch for Guest login (from "Continue as Guest" button)
            watch(currentUser, (newUser, oldUser) => {
                if (newUser && newUser.is_guest && !oldUser) {
                    console.log('[Guest] Guest mode activated, loading dashboard...');
                    loadDashboard();
                }
            });
        });

        return {
            currentTab, marsList: sortedMarsList, sortedMarsList, stats, groupStats, cbInput, cbResult, loadingCB, analyzeCB,
            portfolioCBs, loadingPortfolioCBs, fetchPortfolioCBs, resultTab,
            getActionColor, getBorderColor, sim, recalculate, formatCurrency, detailStock, openDetail,
            renderRaceChart, playRace, pauseRace, resetRace, sortBy, getSortIcon, raceMetric,
            animationFrames, currentFrameIndex, seekToFrame, isCalculating,
            // Portfolio
            portfolioGroups, selectedGroupId, groupTargets, showAddGroup, newGroupName,
            newTargetId, newTargetName, showTxForm, newTx,
            fetchGroups, createGroup, deleteGroup, selectGroup, addTarget, deleteTarget, addTransaction,
            // Transaction History
            showTxHistory, txHistory, openHistory, deleteTx, openEditTx,
            // Dividend tracking
            dividendCash, syncingDividends, syncDividends, fetchDividendCash,
            // Trend Dashboard & My Race
            trendData, assetGroups, expandedGroup, selectedMonth, maxTrendCost, portfolioRaceData,
            fetchTrendData, getGroupTotal, playPortfolioRace, pausePortfolioRace, fetchPortfolioRaceData,
            // Leaderboard
            // Leaderboard & Profile
            leaderboard, loadingLadder, newNickname, updateProfile, copyPublicLink,
            showProfileModal, profileData, openProfile, getDonutGradient, syncStats,
            showDivDetails, currentYear, raceConfig, // Dividend Modal State & Race Config
            // Settings System
            showSettings, appSettings, isPremium, toggleGMMode, saveSettings, exportToExcel, t,
            // Feedback System
            feedbackForm, feedbackSubmitting, feedbackSuccess, submitFeedback,
            availableLanguages,
            // Notifications System
            showNotifications, notifications, unreadCount, markAllRead, clearNotifications, markAsRead, mobileMenuOpen,
            // AI Copilot
            showChat, chatInput, isChatLoading, chatHistory, sendMessage,
            // Auth & Guest Mode
            currentUser, isGuest, GUEST_LIMITS,
            // Admin Dashboard (GM Only)
            adminMetrics, adminLoading, adminError, fetchAdminMetrics,
            feedbackList, feedbackStats, fetchFeedbackList, updateFeedbackStatus, copyFeedback, updateFeedbackNotes,
            // System Operations
            crawlerRunning, triggerCrawl, triggerBackup, triggerPrewarmRefresh,
            backendUrl
        };
    }
}).mount('#app')
