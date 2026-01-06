import { createApp, ref, onMounted, computed, watch, nextTick } from '/static/vendor/vue.esm-browser.js'

createApp({
    setup() {
        const currentUser = ref(null); // Auth State
        const currentTab = ref('mars');
        const rawMarsData = ref([]);
        const rawRaceData = ref([]);
        const marsList = ref([]); // Processed
        const detailStock = ref(null); // Selected for Modal
        const cbInput = ref('6533');
        const cbResult = ref(null);
        const loadingCB = ref(false);

        // ========== NOTIFICATIONS SYSTEM ==========
        const showNotifications = ref(false);
        const notifications = ref([{ message: 'Welcome to Martian Investment! 🚀', time: 'Now', read: false }]);
        const unreadCount = computed(() => notifications.value.filter(n => !n.read).length);
        const markAllRead = () => { notifications.value.forEach(n => n.read = true); };
        const clearNotifications = () => { notifications.value = []; showNotifications.value = false; };
        const deleteNotification = (idx) => { notifications.value.splice(idx, 1); };
        const addNotification = (msg) => {
            notifications.value.unshift({
                message: msg, time: new
                    Date().toLocaleTimeString(), read: false
            });
        };

        const checkSystemAlerts = async () => {
            try {
                const res = await fetch('/api/notifications/check');
                if (!res.ok) return;
                const alerts = await res.json();
                alerts.forEach(alert => {
                    // Check if duplicate? Simplified: just add.
                    addNotification(alert.message);
                });
                if (alerts.length > 0) {
                    showNotifications.value = true; // Auto-open if alerts found
                }
            } catch (e) { console.error('Alert check failed', e); }
        };

        // ========== CB PORTFOLIO ==========
        const portfolioCBs = ref([]);
        const loadingPortfolioCBs = ref(false);
        const fetchPortfolioCBs = async () => {
            loadingPortfolioCBs.value = true;
            try {
                const res = await fetch('/api/cb/portfolio');
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

            // Build Context
            const context = `
        Portfolio Summary:
        - Total Groups: ${portfolioGroups.value.length}
        - Total Value: ${formatCurrency(stats.value?.totalValue || 0)}
        - Total Cost: ${formatCurrency(stats.value?.totalCost || 0)}
        - Total P/L: ${formatCurrency(stats.value?.totalPL || 0)}
        - Premium User: ${isPremium.value}
        `;

            try {
                const res = await fetch('/api/chat', {
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
                const res = await fetch('/api/notifications/check');
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
        const isPremium = computed(() => appSettings.value.gmMode);



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

        // Sorting Logic
        const sortedMarsList = computed(() => {
            return [...marsList.value].sort((a, b) => {
                let valA = a[sortKey.value];
                let valB = b[sortKey.value];

                // Handle numbers
                if (typeof valA === 'string' && !valA.includes('%')) valA = parseFloat(valA) || valA;
                if (typeof valB === 'string' && !valB.includes('%')) valB = parseFloat(valB) || valB;

                if (valA < valB) return sortDesc.value ? 1 : -1; if (valA > valB) return sortDesc.value ? -1 : 1;
                return 0;
            });
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
        const exportToCSV = () => {
            const dataToExport = isPremium.value ? sortedMarsList.value : rawMarsData.value;
            const headers = ['Stock ID', 'Name', 'CAGR %', 'Valid Years', 'Final Value ($)', 'Total ROI %'];
            let csvContent = '# Martian Investment Export\n';
            csvContent += '# Export Date: ' + new Date().toISOString() + '\n';
            csvContent += '# Simulation: Start Year=' + sim.value.startYear + ', Principal=$' + sim.value.principal
                + ', Annual Contrib=$' + sim.value.contribution + '\n';
            csvContent += '# Tier: ' + (isPremium.value ? 'Premium (Filtered)' : 'Free (Raw)') + '\n';
            csvContent += '# ---\n';
            csvContent += headers.join(',') + '\n';
            dataToExport.forEach(stock => {
                const row = [
                    stock.id,
                    '"' + (stock.name || '') + '"',
                    stock.cagr_pct || stock.cagr || 0,
                    stock.valid_years || 0,
                    stock.finalValue ? Math.round(stock.finalValue) : 0,
                    stock.totalROI || 0
                ];
                csvContent += row.join(',') + '\n';
            });
            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = 'martian_export_' + (isPremium.value ? 'filtered' : 'raw') + '_' + Date.now() + '.csv';
            link.click();
            addNotification('📥 Exported ' + dataToExport.length + ' stocks to CSV');
        };

        const fetchMars = async (year) => {
            try {
                // Default to 2006 if not provided
                const queryYear = year || sim.value.startYear || 2006;
                const [res1, res2] = await Promise.all([
                    fetch('/api/results'),
                    fetch(`/api/race-data?start_year=${queryYear}`)
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
                        value: record.wealth || record.value, // Backend now provides 'wealth'
                        cost: 0,
                        roi: record.roi,
                        cagr: 0,
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
                        cagr = ((Math.pow(final / sim.value.principal, 1 / years) - 1) * 100).toFixed(2);
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

        // D3.js Bar Chart Race Configuration
        const raceConfig = {
            barHeight: 22,
            barPadding: 2,
            topN: 25, // User requested 25 instead of 15
            duration: 1200, // Slower animation (user request)
            margin: { top: 60, right: 20, bottom: 80, left: 200 }
        };

        // Dynamic Race Chart (D3.js with smooth transitions)
        const renderRaceChart = () => {
            console.log('[D3 Race] renderRaceChart called. rawMarsData:', rawMarsData.value.length);
            if (!rawMarsData.value.length) {
                console.log('[D3 Race] No rawMarsData, returning');
                return;
            }
            raceRendered.value = false;

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
                if (!path) return;

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
                        raceMap.get(p.year).push({
                            id: p.id,
                            name: stockNameMap.get(p.id) || p.id,
                            // Use per-year calculated CAGR for racing animation
                            value: raceMetric.value === 'wealth' ? p.value : p.cagr
                        });
                    }
                });
            });

            const years = Array.from(raceMap.keys()).filter(y => raceMap.get(y).length > 0).sort((a, b) => a - b);

            // Build keyframes: each frame = { year, data: [ { id, name, value, rank } ] }
            const keyframes = years.map(year => {
                const sorted = raceMap.get(year).sort((a, b) => b.value - a.value).slice(0, raceConfig.topN);
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
            const height = raceConfig.topN * (raceConfig.barHeight + raceConfig.barPadding) + raceConfig.margin.top
                + raceConfig.margin.bottom;

            console.log('[D3 Race] Container dimensions:', width, 'x', height, 'd3 defined:', typeof d3);

            const svg = d3.select(container)
                .append('svg')
                .attr('width', width)
                .attr('height', height)
                .attr('viewBox', `0 0 ${width} ${height}`)
                .style('background', 'transparent');

            console.log('[D3 Race] SVG created:', svg.node());

            // Scales
            const xScale = d3.scaleLinear().range([raceConfig.margin.left, width - raceConfig.margin.right]);
            const yScale = d3.scaleLinear().range([raceConfig.margin.top, height - raceConfig.margin.bottom -
                raceConfig.barHeight]);
            const colorScale = d3.scaleOrdinal(d3.schemeTableau10);

            // X-Axis
            const xAxis = svg.append('g')
                .attr('class', 'x-axis')
                .attr('transform', `translate(0, ${raceConfig.margin.top - 10})`);

            // Year Label (big watermark)
            const yearLabel = svg.append('text')
                .attr('class', 'year-label')
                .attr('x', width - 50)
                .attr('y', height - 30)
                .attr('text-anchor', 'end')
                .attr('fill', 'rgba(255,255,255,0.15)')
                .attr('font-size', '100px')
                .attr('font-weight', '900')
                .attr('font-family', 'Inter, sans-serif');

            // Bar Group
            const barsGroup = svg.append('g').attr('class', 'bars');
            const labelsGroup = svg.append('g').attr('class', 'labels');
            const valuesGroup = svg.append('g').attr('class', 'values');

            // Update function for each frame
            window.updateRaceFrame = (frameData, instant = false) => {
                const dur = instant ? 0 : raceConfig.duration;
                const data = frameData.data;
                const maxValue = d3.max(data, d => d.value) || 1;

                xScale.domain([0, maxValue * 1.1]);
                yScale.domain([0, raceConfig.topN - 1]);

                // X-Axis transition
                xAxis.transition().duration(dur).call(d3.axisTop(xScale).ticks(5).tickFormat(d => raceMetric.value ===
                    'wealth' ? formatCurrency(d) : `${d.toFixed(0)}%`));
                xAxis.selectAll('text').attr('fill', '#888');
                xAxis.selectAll('line, path').attr('stroke', '#333');

                // Year watermark
                yearLabel.text(frameData.year);

                // BARS with key-based join for object constancy
                const bars = barsGroup.selectAll('rect').data(data, d => d.id);

                bars.exit().transition().duration(dur).attr('width', 0).remove();

                bars.enter()
                    .append('rect')
                    .attr('x', raceConfig.margin.left)
                    .attr('y', d => yScale(d.rank))
                    .attr('height', raceConfig.barHeight)
                    .attr('fill', d => colorScale(d.id))
                    .attr('rx', 4)
                    .attr('width', 0)
                    .merge(bars)
                    .transition()
                    .duration(dur)
                    .ease(d3.easeCubicInOut)
                    .attr('y', d => yScale(d.rank)) // SMOOTH Y transition
                    .attr('width', d => xScale(d.value) - raceConfig.margin.left);

                // LABELS (stock names on left)
                const labels = labelsGroup.selectAll('text').data(data, d => d.id);

                labels.exit().transition().duration(dur).style('opacity', 0).remove();

                labels.enter()
                    .append('text')
                    .attr('x', raceConfig.margin.left - 5)
                    .attr('y', d => yScale(d.rank) + raceConfig.barHeight / 2)
                    .attr('text-anchor', 'end')
                    .attr('fill', '#fff')
                    .attr('font-size', '12px')
                    .attr('dominant-baseline', 'middle')
                    .style('opacity', 0)
                    .merge(labels)
                    .transition()
                    .duration(dur)
                    .ease(d3.easeCubicInOut)
                    .attr('y', d => yScale(d.rank) + raceConfig.barHeight / 2) // SMOOTH Y transition
                    .style('opacity', 1)
                    .text(d => `${d.name} (${d.id})`);

                // VALUES (inside bars on right)
                const values = valuesGroup.selectAll('text').data(data, d => d.id);

                values.exit().transition().duration(dur).style('opacity', 0).remove();

                values.enter()
                    .append('text')
                    .attr('x', d => xScale(d.value) - 5)
                    .attr('y', d => yScale(d.rank) + raceConfig.barHeight / 2)
                    .attr('text-anchor', 'end')
                    .attr('fill', '#000')
                    .attr('font-size', '11px')
                    .attr('font-weight', 'bold')
                    .attr('dominant-baseline', 'middle')
                    .style('opacity', 0)
                    .merge(values)
                    .transition()
                    .duration(dur)
                    .ease(d3.easeCubicInOut)
                    .attr('x', d => xScale(d.value) - 5)
                    .attr('y', d => yScale(d.rank) + raceConfig.barHeight / 2) // SMOOTH Y transition
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

        const openDetail = async (stock) => {
            detailStock.value = stock; // Show immediately with basic data
            resultTab.value = 'wealth';

            try {
                // Fetch Detailed History
                const res = await fetch(`/api/stock/${stock.id}/history`);
                const history = await res.json();

                if (Array.isArray(history) && history.length > 0) {
                    // Recalculate Wealth Path using Share Logic
                    const newPath = simulateShareAccumulation(stock.id, history);

                    // Update detailStock with more accurate data
                    detailStock.value = {
                        ...stock,
                        wealthPath: newPath,
                        finalValue: newPath[newPath.length - 1].value,
                        totalROI: newPath[newPath.length - 1].roi.toFixed(2),
                        cagr: newPath[newPath.length - 1].cagr
                    };
                }
            } catch (e) { console.error('Sim error', e); }

            nextTick(() => renderDetailChart(detailStock.value));
        };

        // Reactive Chart Update
        watch(resultTab, () => {
            if (detailStock.value) {
                renderDetailChart(detailStock.value);
            }
        });

        const renderDetailChart = (stock) => {
            const isWealth = resultTab.value === 'wealth';
            const trace = {
                x: stock.wealthPath.map(d => d.year),
                y: isWealth ? stock.wealthPath.map(d => d.value) : stock.wealthPath.map(d => d.dividend),
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

        const analyzeCB = async () => {
            loadingCB.value = true;
            cbResult.value = null;
            try {
                const res = await fetch(`/api/cb/analyze?code=${cbInput.value}`);
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
                const res = await fetch('/api/portfolio/cash');
                dividendCash.value = await res.json();
            } catch (e) { console.error('Fetch dividend cash error:', e); }
        };

        // Sync dividends
        const syncDividends = async () => {
            syncingDividends.value = true;
            try {
                const res = await fetch('/api/portfolio/sync-dividends', { method: 'POST' });
                const result = await res.json();
                console.log('Synced dividends:', result);
                await fetchDividendCash();
                alert('Synced ' + (result.synced_count || 0) + ' new dividends!');
            } catch (e) { console.error('Sync dividends error:', e); }
            syncingDividends.value = false;
        };

        // Fetch all groups
        const fetchGroups = async () => {
            try {
                const res = await fetch('/api/portfolio/groups');
                portfolioGroups.value = await res.json();
                // Auto-select first group
                if (portfolioGroups.value.length && !selectedGroupId.value) {
                    selectGroup(portfolioGroups.value[0].id);
                }
            } catch (e) { console.error('Fetch groups error:', e); }
        };

        // Create group
        const createGroup = async () => {
            if (!newGroupName.value.trim()) return;
            try {
                const res = await fetch('/api/portfolio/groups', {
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
            try {
                await fetch(`/api/portfolio/groups/${groupId}`, { method: 'DELETE' });
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
            try {
                const res = await fetch(`/api/portfolio/groups/${groupId}/targets`);
                const targets = await res.json();

                // Collect all stock IDs for batch price fetch
                const stockIds = targets.map(t => t.stock_id).join(',');

                // Fetch live prices (parallel)
                let livePrices = {};
                if (stockIds) {
                    try {
                        const priceRes = await fetch(`/api/portfolio/prices?stock_ids=${stockIds}`);
                        livePrices = await priceRes.json();
                    } catch (e) { console.warn('Live price fetch failed:', e); }
                }

                // Fetch summary for each target with live price
                for (const t of targets) {
                    const livePrice = livePrices[t.stock_id]?.price || null;
                    t.livePrice = livePrices[t.stock_id] || { price: 0, change: 0, change_pct: 0 };

                    // Fetch summary with current price for P/L calculation
                    const sumUrl = livePrice
                        ? `/api/portfolio/targets/${t.id}/summary?current_price=${livePrice}`
                        : `/api/portfolio/targets/${t.id}/summary`;
                    const sumRes = await fetch(sumUrl);
                    t.summary = await sumRes.json();
                }
                groupTargets.value = targets;
            } catch (e) { console.error('Load targets error:', e); }
        };

        // Add target
        const addTarget = async () => {
            if (!newTargetId.value.trim() || !selectedGroupId.value) return;
            try {
                // Optimization: Lookup name from Mars Strategy list if available
                let finalName = newTargetName.value.trim();
                if (!finalName && marsList.value.length) {
                    const found = marsList.value.find(s => s.id === newTargetId.value.trim());
                    if (found) finalName = found.name;
                }

                const res = await fetch(`/api/portfolio/groups/${selectedGroupId.value}/targets`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ stock_id: newTargetId.value.trim(), stock_name: finalName || null })
                });
                if (res.ok) {
                    newTargetId.value = '';
                    newTargetName.value = '';
                    await selectGroup(selectedGroupId.value);
                }
            } catch (e) { console.error('Add target error:', e); }
        };

        // Delete target
        const deleteTarget = async (targetId) => {
            if (!confirm('Delete this stock and all transactions?')) return;
            try {
                await fetch(`/api/portfolio/targets/${targetId}`, { method: 'DELETE' });
                await selectGroup(selectedGroupId.value);
            } catch (e) { console.error('Delete target error:', e); }
        };

        // Add or Update transaction
        const addTransaction = async () => {
            if (!showTxForm.value || !newTx.value.shares || !newTx.value.price) return;

            const isEdit = !!newTx.value.id;
            const url = isEdit
                ? `/api/portfolio/transactions/${newTx.value.id}`
                : `/api/portfolio/targets/${showTxForm.value}/transactions`;
            const method = isEdit ? 'PUT' : 'POST';

            try {
                const res = await fetch(url, {
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
                }
            } catch (e) { console.error('Transaction error:', e); }
        };

        // Transaction History
        const showTxHistory = ref(null); // target_id
        const txHistory = ref([]);

        const fetchTxHistory = async (targetId) => {
            try {
                const res = await fetch(`/api/portfolio/targets/${targetId}/transactions`);
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
                await fetch(`/api/portfolio/transactions/${txId}`, { method: 'DELETE' });
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
                // Fetch trend history
                const trendRes = await fetch('/api/portfolio/trend?months=12');
                trendData.value = await trendRes.json();
                if (trendData.value.length) {
                    selectedMonth.value = trendData.value[trendData.value.length - 1]?.month;
                }

                // Fetch asset groups
                const groupRes = await fetch('/api/portfolio/by-type');
                const groups = await groupRes.json();
                assetGroups.value = groups;

                // Collect all stock IDs to fetch current prices
                const allTargets = [...(groups.stock || []), ...(groups.etf || []), ...(groups.cb || [])];
                const ids = allTargets.map(t => t.stock_id).filter(id => id).join(',');

                if (ids) {
                    const priceRes = await fetch(`/api/portfolio/prices?stock_ids=${ids}`);
                    trendLivePrices.value = await priceRes.json();
                }

                // Fetch race data
                const raceRes = await fetch('/api/portfolio/race-data');
                portfolioRaceData.value = await raceRes.json();
            } catch (e) { console.error('Fetch trend error:', e); }
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
                const raceRes = await fetch('/api/portfolio/race-data');
                portfolioRaceData.value = await raceRes.json();

                // Also fetch asset groups for stats
                const groupRes = await fetch('/api/portfolio/by-type');
                assetGroups.value = await groupRes.json();
            } catch (e) { console.error('Fetch race data error:', e); }
        };

        // ============== LEADERBOARD & PROFILE ==============
        const leaderboard = ref([]);
        const loadingLadder = ref(false);
        const newNickname = ref('');
        const showProfileModal = ref(false);
        const profileData = ref(null);

        // Dividend Modal State
        const showDivDetails = ref(null);

        const currentYear = new Date().getFullYear();

        const fetchLeaderboard = async () => {
            loadingLadder.value = true;
            try {
                const res = await fetch('/api/leaderboard');
                leaderboard.value = await res.json();
            } catch (e) { console.error('Leaderboard error:', e); }
            loadingLadder.value = false;
        };

        const openProfile = async (userId) => {
            try {
                const res = await fetch(`/api/public/profile/${userId}`);
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
                const res = await fetch('/api/portfolio/sync-stats', { method: 'POST' });
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
                const res = await fetch('/api/auth/profile', {
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
                checkSystemAlerts(); // Check for Premium Alerts

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
                    }
                });
            };

            // Check Auth
            try {
                const res = await fetch('/auth/me');
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
        });

        return {
            currentTab, marsList: sortedMarsList, stats, groupStats, cbInput, cbResult, loadingCB, analyzeCB,
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
            showSettings, appSettings, isPremium, toggleGMMode, saveSettings, exportToCSV, t,
            availableLanguages,
            // Notifications System
            showNotifications, notifications, unreadCount, markAllRead, clearNotifications, deleteNotification,
            addNotification,
            // AI Copilot
            showChat, chatInput, isChatLoading, chatHistory, sendMessage,
            // Auth
            currentUser
        };
    }
}).mount('#app')
