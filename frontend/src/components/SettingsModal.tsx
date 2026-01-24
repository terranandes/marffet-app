"use client";

import { useState, useEffect } from "react";

interface User {
    id: string | null;
    email?: string;
    name?: string;
    nickname?: string;
    picture?: string;
    is_admin?: boolean;
}

interface SettingsModalProps {
    isOpen: boolean;
    onClose: () => void;
    user: User | null;
    onUpdateUser: () => void; // Trigger parent re-fetch
}

// Simple Accordion Component
const Accordion = ({ title, children, defaultOpen = false }: { title: React.ReactNode, children: React.ReactNode, defaultOpen?: boolean }) => {
    const [isOpen, setIsOpen] = useState(defaultOpen);
    return (
        <div className="border border-white/10 rounded-xl overflow-hidden bg-white/5">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="w-full flex items-center justify-between p-4 text-left hover:bg-white/5 transition"
            >
                <div className="font-bold text-gray-200">{title}</div>
                <div className={`transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}>▼</div>
            </button>
            {isOpen && (
                <div className="p-4 border-t border-white/10 text-sm text-gray-400 space-y-2 bg-black/20">
                    {children}
                </div>
            )}
        </div>
    );
};

export default function SettingsModal({ isOpen, onClose, user, onUpdateUser }: SettingsModalProps) {
    const [activeTab, setActiveTab] = useState("profile"); // profile, preferences, api, help

    // Form States
    const [nickname, setNickname] = useState(user?.nickname || "");
    const [apiKey, setApiKey] = useState("");
    const [language, setLanguage] = useState("en");
    const [region, setRegion] = useState("TW"); // Fixed to TW
    const [defaultPage, setDefaultPage] = useState("/"); // Default to Dashboard
    const [isPremium, setIsPremium] = useState(false);

    // Feedback State
    const [feedbackCategory, setFeedbackCategory] = useState("settings");
    const [feedbackType, setFeedbackType] = useState("suggestion");
    const [feedbackMessage, setFeedbackMessage] = useState("");

    // Status
    const [loading, setLoading] = useState(false);
    const [syncLoading, setSyncLoading] = useState(false);
    const [msg, setMsg] = useState<{ type: 'success' | 'error', text: string } | null>(null);

    // Initialize from LocalStorage & User Props
    useEffect(() => {
        if (isOpen) {
            setNickname(user?.nickname || "");
            setApiKey(localStorage.getItem("martian_api_key") || "");
            setLanguage(localStorage.getItem("martian_lang") || "en");
            setRegion(localStorage.getItem("martian_region") || "TW");
            setDefaultPage(localStorage.getItem("martian_default_page") || "/");
            setIsPremium(localStorage.getItem("martian_premium") === "true");
            setMsg(null);
        }
    }, [isOpen, user]);

    const handleSaveProfile = async () => {
        setLoading(true);
        setMsg(null);
        try {
            const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
            const res = await fetch(`${API_URL}/api/auth/profile`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ nickname }),
                credentials: "include"
            });

            if (res.ok) {
                setMsg({ type: "success", text: "Profile updated successfully" });
                onUpdateUser(); // Refresh parent user state
            } else {
                setMsg({ type: "error", text: "Failed to update profile" });
            }
        } catch (e) {
            setMsg({ type: "error", text: "Network error" });
        }
        setLoading(false);
    };

    const handleSyncStats = async () => {
        setSyncLoading(true);
        setMsg(null);
        try {
            const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
            const res = await fetch(`${API_URL}/api/portfolio/sync-stats`, {
                method: "POST",
                credentials: "include"
            });
            if (res.ok) {
                const data = await res.json();
                setMsg({ type: "success", text: `Rank Synced! ROI: ${data.roi}%` });
            } else {
                setMsg({ type: "error", text: "Sync failed" });
            }
        } catch (e) {
            setMsg({ type: "error", text: "Network error" });
        }
        setSyncLoading(false);
    };

    const handleSavePreferences = () => {
        localStorage.setItem("martian_lang", language);
        localStorage.setItem("martian_region", region);
        localStorage.setItem("martian_default_page", defaultPage);
        localStorage.setItem("martian_premium", String(isPremium));
        setMsg({ type: "success", text: "Preferences saved (reload to apply)" });
    };

    const handleSaveKey = () => {
        localStorage.setItem("martian_api_key", apiKey);
        setMsg({ type: "success", text: "API Key saved securely" });
    };

    const handleSendFeedback = async () => {
        if (!feedbackMessage.trim()) {
            setMsg({ type: "error", text: "Please enter a message" });
            return;
        }
        setLoading(true);
        try {
            const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
            const res = await fetch(`${API_URL}/api/feedback`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    feature_category: feedbackCategory,
                    feedback_type: feedbackType,
                    message: feedbackMessage
                }),
                credentials: "include"
            });
            if (res.ok) {
                setMsg({ type: "success", text: "Feedback sent! We appreciate it." });
                setFeedbackMessage("");
            } else {
                setMsg({ type: "error", text: "Failed to send feedback" });
            }
        } catch (e) {
            setMsg({ type: "error", text: "Network error" });
        }
        setLoading(false);
    };

    if (!isOpen || !user) return null;

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/80 backdrop-blur-md"
                onClick={onClose}
            />

            {/* Modal */}
            <div className="relative w-full max-w-2xl bg-[#0e1117] border border-cyan-500/30 rounded-2xl shadow-[0_0_50px_rgba(0,242,234,0.1)] overflow-hidden flex flex-col max-h-[90vh]">

                {/* Header */}
                <div className="p-6 border-b border-white/10 flex justify-between items-center bg-gradient-to-r from-[#0e1117] to-[#1a1f2e]">
                    <h2 className="text-xl font-bold text-white flex items-center gap-2">
                        <span className="text-2xl">⚙️</span> Settings
                    </h2>
                    <button onClick={onClose} className="text-zinc-400 hover:text-white transition hover:rotate-90 duration-300">
                        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {/* Body */}
                <div className="flex flex-1 overflow-hidden">
                    {/* Sidebar Tabs */}
                    <div className="w-52 border-r border-white/10 bg-black/20 p-4 flex flex-col gap-2">
                        {[
                            { id: 'profile', label: 'Profile', icon: '👤' },
                            { id: 'preferences', label: 'Preferences', icon: '🌍' },
                            { id: 'api', label: 'Ai Keys', icon: '🔑' },
                            { id: 'help', label: 'Help', icon: '📚' },
                            { id: 'support', label: 'Support', icon: '💬' },
                        ].map(tab => (
                            <button
                                key={tab.id}
                                onClick={() => { setActiveTab(tab.id); setMsg(null); }}
                                className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-bold transition-all relative overflow-hidden ${activeTab === tab.id
                                    ? "bg-cyan-500/10 text-cyan-400 border border-cyan-500/50 shadow-[0_0_15px_rgba(34,211,238,0.2)]"
                                    : "text-zinc-400 hover:text-white hover:bg-white/5 border border-transparent"
                                    }`}
                            >
                                <span className="relative z-10">{tab.icon}</span>
                                <span className="relative z-10">{tab.label}</span>
                                {activeTab === tab.id && <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 to-transparent" />}
                            </button>
                        ))}
                    </div>

                    {/* Content Area */}
                    <div className="flex-1 p-8 overflow-y-auto bg-gradient-to-b from-[#0e1117] to-[#13161c]">

                        {/* Messages */}
                        {msg && (
                            <div className={`mb-6 p-4 rounded-xl border flex items-center gap-3 animate-fade-in ${msg.type === 'success'
                                ? 'bg-green-500/10 border-green-500/30 text-green-400'
                                : 'bg-red-500/10 border-red-500/30 text-red-400'
                                }`}>
                                {msg.type === 'success' ? '✅' : '❌'} {msg.text}
                            </div>
                        )}

                        {/* PROFILE TAB */}
                        {activeTab === 'profile' && (
                            <div className="space-y-8 animate-fade-in">
                                <h3 className="text-lg font-bold text-white mb-4 border-b border-white/10 pb-2">User Profile</h3>

                                <div className="flex items-center gap-6 p-6 rounded-2xl bg-white/5 border border-white/10">
                                    <div className="relative">
                                        <img
                                            src={user.picture}
                                            className="w-20 h-20 rounded-full border-2 border-cyan-500 shadow-[0_0_20px_rgba(34,211,238,0.2)]"
                                        />
                                        {user.is_admin && <div className="absolute -bottom-2 -right-2 text-xl">👑</div>}
                                    </div>
                                    <div>
                                        <div className="text-2xl font-bold text-white">{user.name}</div>
                                        <div className="text-sm text-zinc-500 font-mono">{user.email}</div>
                                        {user.is_admin && (
                                            <span className="mt-2 inline-block px-3 py-1 rounded-full text-[10px] uppercase tracking-wider font-bold bg-purple-500/20 text-purple-400 border border-purple-500/30">
                                                Game Master
                                            </span>
                                        )}
                                    </div>
                                </div>

                                <div className="space-y-6">
                                    <div className="space-y-2">
                                        <label className="text-xs font-bold text-cyan-400 uppercase tracking-wider">Display Nickname</label>
                                        <div className="flex gap-2">
                                            <input
                                                type="text"
                                                value={nickname}
                                                onChange={(e) => setNickname(e.target.value)}
                                                className="flex-1 bg-black/40 border border-zinc-700 rounded-xl px-4 py-3 text-white focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 outline-none transition"
                                                placeholder="Enter your nickname"
                                            />
                                            <button
                                                onClick={handleSaveProfile}
                                                disabled={loading}
                                                className="px-6 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 text-white font-bold rounded-xl hover:shadow-[0_0_20px_rgba(34,211,238,0.4)] transition disabled:opacity-50"
                                            >
                                                {loading ? "..." : "Save"}
                                            </button>
                                        </div>
                                        <p className="text-xs text-zinc-600">Visible on public leaderboards.</p>
                                    </div>

                                    {/* Leaderboard Rank Section */}
                                    <div className="pt-6 border-t border-white/10">
                                        <label className="text-xs font-bold text-yellow-500 uppercase tracking-wider mb-2 block">🏆 Leaderboard Rank</label>
                                        <div className="flex justify-between items-center p-4 rounded-xl bg-yellow-500/5 border border-yellow-500/20">
                                            <p className="text-xs text-gray-400">Update your wealth stats on the global leaderboard.</p>
                                            <button
                                                onClick={handleSyncStats}
                                                disabled={syncLoading}
                                                className="bg-yellow-500/20 text-yellow-400 hover:bg-yellow-500/40 px-4 py-2 rounded-lg text-sm font-bold border border-yellow-500/50 transition hover:shadow-[0_0_15px_rgba(234,179,8,0.3)] disabled:opacity-50"
                                            >
                                                {syncLoading ? "Syncing..." : "Sync Now"}
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* PREFERENCES TAB */}
                        {activeTab === 'preferences' && (
                            <div className="space-y-8 animate-fade-in">
                                <h3 className="text-lg font-bold text-white mb-4 border-b border-white/10 pb-2">App Preferences</h3>

                                {/* Start Page Selector */}
                                <div className="space-y-2">
                                    <label className="text-xs font-bold text-cyan-400 uppercase tracking-wider">Start Page</label>
                                    <select
                                        className="w-full bg-black/40 border border-zinc-700 rounded-xl px-4 py-3 text-white focus:border-cyan-500 outline-none"
                                        value={defaultPage}
                                        onChange={(e) => setDefaultPage(e.target.value)}
                                    >
                                        <option value="/">🏠 Dashboard</option>
                                        <option value="/portfolio">📊 Portfolio</option>
                                        <option value="/mars">🚀 Mars Strategy</option>
                                        <option value="/viz">📉 Visualizations</option>
                                        <option value="/cb">💹 Convertible Bond</option>
                                    </select>
                                    <p className="text-xs text-zinc-600">Loads automatically on visit.</p>
                                </div>

                                {/* Region Selector (Fixed) */}
                                <div className="space-y-2">
                                    <label className="text-xs font-bold text-cyan-400 uppercase tracking-wider">Region Format</label>
                                    <div className="grid grid-cols-1 gap-2">
                                        <div className="p-3 bg-cyan-900/20 border border-cyan-500/50 rounded-xl flex items-center justify-between">
                                            <div className="flex items-center gap-3">
                                                <span className="text-2xl">🇹🇼</span>
                                                <div className="font-bold text-white">Taiwan (TWD)</div>
                                            </div>
                                            <div className="text-cyan-400 text-xs font-bold px-2 py-1 bg-cyan-900/50 rounded border border-cyan-500/30">Active</div>
                                        </div>
                                        <div className="p-3 bg-zinc-800/20 border border-zinc-800 rounded-xl flex items-center justify-between opacity-50 cursor-not-allowed">
                                            <div className="flex items-center gap-3">
                                                <span className="text-2xl">🇨🇳</span>
                                                <div className="font-bold text-gray-500">China</div>
                                            </div>
                                        </div>
                                        <div className="p-3 bg-zinc-800/20 border border-zinc-800 rounded-xl flex items-center justify-between opacity-50 cursor-not-allowed">
                                            <div className="flex items-center gap-3">
                                                <span className="text-2xl">🇺🇸</span>
                                                <div className="font-bold text-gray-500">USA</div>
                                            </div>
                                        </div>
                                    </div>
                                    <p className="text-xs text-zinc-600 mt-1">Global regions coming in Q4 2026.</p>
                                </div>

                                {/* GM Controls */}
                                {user?.is_admin && (
                                    <div className="space-y-2">
                                        <label className="text-xs font-bold text-purple-400 uppercase tracking-wider">GM Controls</label>
                                        <div className="flex items-center gap-3 p-3 bg-purple-900/10 border border-purple-500/30 rounded-xl">
                                            <div className="flex-1">
                                                <div className="font-bold text-white">Premium Status</div>
                                                <div className="text-xs text-zinc-400">Unlock advanced features for testing</div>
                                            </div>
                                            <button
                                                onClick={() => setIsPremium(!isPremium)}
                                                className={`w-12 h-6 rounded-full transition-all duration-300 relative ${isPremium
                                                    ? 'bg-gradient-to-r from-amber-400 to-yellow-500 shadow-[0_0_12px_rgba(255,215,0,0.4)]'
                                                    : 'bg-zinc-700'
                                                    }`}
                                            >
                                                <div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-all duration-300 shadow-md ${isPremium ? 'left-7' : 'left-1'
                                                    }`} />
                                            </button>
                                        </div>
                                    </div>
                                )}

                                <button
                                    onClick={handleSavePreferences}
                                    className="w-full px-6 py-3 bg-zinc-800 hover:bg-zinc-700 text-white font-bold rounded-xl transition border border-white/5"
                                >
                                    Save Preferences
                                </button>
                            </div>
                        )}

                        {/* API KEY TAB */}
                        {activeTab === 'api' && (
                            <div className="space-y-8 animate-fade-in">
                                <h3 className="text-lg font-bold text-white mb-4 border-b border-white/10 pb-2">AI Integration</h3>

                                <div className="p-4 bg-teal-500/10 border border-teal-500/20 rounded-xl text-sm text-teal-200 mb-6">
                                    💡 <strong>Gemini Copilot</strong> requires a valid API Key.
                                    <br /><span className="text-teal-400/70 text-xs">The default key is provided by the system, but you can override it here for higher rate limits.</span>
                                </div>

                                <div className="space-y-2">
                                    <label className="text-xs font-bold text-cyan-400 uppercase tracking-wider">Gemini API Key</label>
                                    <input
                                        type="password"
                                        value={apiKey}
                                        onChange={(e) => setApiKey(e.target.value)}
                                        className="w-full bg-black/40 border border-zinc-700 rounded-xl px-4 py-3 text-white focus:border-cyan-500 outline-none font-mono"
                                        placeholder="AIzaSy..."
                                    />
                                </div>

                                <button
                                    onClick={handleSaveKey}
                                    className="w-full px-6 py-3 bg-zinc-800 hover:bg-zinc-700 text-white font-bold rounded-xl transition border border-white/5"
                                >
                                    Save Key
                                </button>
                            </div>
                        )}

                        {/* HELP TAB */}
                        {activeTab === 'help' && (
                            <div className="space-y-6 animate-fade-in">
                                <h3 className="text-lg font-bold text-white mb-4 border-b border-white/10 pb-2">Help Center</h3>

                                <div className="mb-6">
                                    <a href="https://github.com/terranandes/martian" target="_blank" rel="noopener noreferrer"
                                        className="p-4 bg-zinc-800/50 hover:bg-zinc-800 border border-zinc-700 rounded-xl transition group flex items-center gap-4">
                                        <div className="text-2xl">📚</div>
                                        <div>
                                            <div className="font-bold text-white group-hover:text-cyan-400 transition">Documentation</div>
                                            <div className="text-xs text-zinc-500">Visit our GitHub Wiki for detailed guides</div>
                                        </div>
                                    </a>
                                </div>

                                <Accordion title={<span className="text-cyan-400 flex items-center gap-2">📖 Feature Guide</span>} defaultOpen={false}>
                                    <div><strong className="text-cyan-300">Mars Strategy:</strong> Search & filter stocks using Top 50 strategy</div>
                                    <div><strong className="text-cyan-300">Bar Chart Race:</strong> Animated wealth growth visualization</div>
                                    <div><strong className="text-cyan-300">Portfolio:</strong> Track real investments with groups & transactions</div>
                                    <div><strong className="text-cyan-300">Trend:</strong> Monthly cost trends and live prices</div>
                                    <div><strong className="text-cyan-300">My Race:</strong> Watch your portfolio stocks compete</div>
                                    <div><strong className="text-cyan-300">AI Copilot:</strong> Get investment advice from Mars AI</div>
                                    <div><strong className="text-cyan-300">Leaderboard:</strong> Community rankings & public profiles</div>
                                </Accordion>

                                <Accordion title={<span className="text-yellow-400 flex items-center gap-2">⭐ Premium Features</span>}>
                                    <div>• <strong>AI Personality:</strong> Ruthless Wealth Manager mode</div>
                                    <div>• <strong>Portfolio Groups:</strong> Up to 30 (vs 11 free)</div>
                                    <div>• <strong>Targets/Group:</strong> Up to 200 (vs 50 free)</div>
                                    <div>• <strong>Transactions:</strong> Up to 1000 (vs 100 free)</div>
                                    <div>• <strong>CB Notifications:</strong> Email alerts</div>
                                    <div>• <strong>Data Export:</strong> Filtered Excel</div>
                                </Accordion>

                                <div className="text-xs text-gray-500 italic text-center">
                                    💳 How to Subscribe: Coming Soon
                                </div>
                            </div>
                        )}

                        {/* SUPPORT TAB */}
                        {activeTab === 'support' && (
                            <div className="space-y-6 animate-fade-in">
                                <h3 className="text-lg font-bold text-white mb-4 border-b border-white/10 pb-2">Support & Feedback</h3>

                                <div className="mb-6">
                                    <a href="mailto:support@martian.com" className="p-4 bg-zinc-800/50 hover:bg-zinc-800 border border-zinc-700 rounded-xl transition group flex items-center gap-4">
                                        <div className="text-2xl">🆘</div>
                                        <div>
                                            <div className="font-bold text-white group-hover:text-cyan-400 transition">Email Support</div>
                                            <div className="text-xs text-zinc-500">Get help directly from our team</div>
                                        </div>
                                    </a>
                                </div>

                                <div className="border-t border-white/10 pt-6">
                                    <h3 className="text-md font-bold text-white mb-4">Send Feedback</h3>
                                    <p className="text-sm text-zinc-400 mb-4">Help us improve the Martian System! Report bugs or suggest features.</p>

                                    <div className="grid grid-cols-2 gap-4 mb-4">
                                        <div className="space-y-2">
                                            <label className="text-xs font-bold text-cyan-400 uppercase tracking-wider">Type</label>
                                            <select
                                                value={feedbackType}
                                                onChange={(e) => setFeedbackType(e.target.value)}
                                                className="w-full bg-black/40 border border-zinc-700 rounded-xl px-4 py-3 text-white focus:border-cyan-500 outline-none"
                                            >
                                                <option value="suggestion">💡 Suggestion</option>
                                                <option value="bug">🐛 Bug Report</option>
                                                <option value="question">❓ Question</option>
                                            </select>
                                        </div>
                                        <div className="space-y-2">
                                            <label className="text-xs font-bold text-cyan-400 uppercase tracking-wider">Category</label>
                                            <select
                                                value={feedbackCategory}
                                                onChange={(e) => setFeedbackCategory(e.target.value)}
                                                className="w-full bg-black/40 border border-zinc-700 rounded-xl px-4 py-3 text-white focus:border-cyan-500 outline-none"
                                            >
                                                <option value="settings">Settings / General</option>
                                                <option value="subscription">Subscription</option>
                                                <option value="mars_strategy">Mars Strategy</option>
                                                <option value="bar_chart_race">Bar Chart Race</option>
                                                <option value="portfolio">Portfolio</option>
                                                <option value="trend">Trend Dashboard</option>
                                                <option value="my_race">My Portfolio Race</option>
                                                <option value="ai_copilot">AI Copilot</option>
                                                <option value="leaderboard">Leaderboard</option>
                                                <option value="other">Other</option>
                                            </select>
                                        </div>
                                    </div>

                                    <div className="space-y-2 mb-4">
                                        <label className="text-xs font-bold text-cyan-400 uppercase tracking-wider">Message</label>
                                        <textarea
                                            value={feedbackMessage}
                                            onChange={(e) => setFeedbackMessage(e.target.value)}
                                            className="w-full h-32 bg-black/40 border border-zinc-700 rounded-xl px-4 py-3 text-white focus:border-cyan-500 outline-none resize-none"
                                            placeholder="Describe your feedback here..."
                                        />
                                    </div>

                                    <button
                                        onClick={handleSendFeedback}
                                        disabled={loading}
                                        className="w-full px-6 py-3 bg-gradient-to-r from-cyan-600 to-blue-600 text-white font-bold rounded-xl hover:shadow-[0_0_20px_rgba(34,211,238,0.4)] transition disabled:opacity-50"
                                    >
                                        {loading ? "Sending..." : "Submit Feedback"}
                                    </button>
                                </div>
                            </div>
                        )}

                    </div>
                </div>
            </div>
        </div>
    );
}
