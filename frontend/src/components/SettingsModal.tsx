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

export default function SettingsModal({ isOpen, onClose, user, onUpdateUser }: SettingsModalProps) {
    const [activeTab, setActiveTab] = useState("profile"); // profile, preferences, api

    // Form States
    const [nickname, setNickname] = useState(user?.nickname || "");
    const [apiKey, setApiKey] = useState("");
    const [language, setLanguage] = useState("en");
    const [region, setRegion] = useState("US");
    const [isPremium, setIsPremium] = useState(false);

    // Feedback State
    const [feedbackCategory, setFeedbackCategory] = useState("settings");
    const [feedbackType, setFeedbackType] = useState("suggestion");
    const [feedbackMessage, setFeedbackMessage] = useState("");

    // Status
    const [loading, setLoading] = useState(false);
    const [msg, setMsg] = useState<{ type: 'success' | 'error', text: string } | null>(null);

    // Initialize from LocalStorage & User Props
    useEffect(() => {
        if (isOpen) {
            setNickname(user?.nickname || "");
            setApiKey(localStorage.getItem("martian_api_key") || "");
            setLanguage(localStorage.getItem("martian_lang") || "en");
            setRegion(localStorage.getItem("martian_region") || "US");
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

    const handleSavePreferences = () => {
        localStorage.setItem("martian_lang", language);
        localStorage.setItem("martian_region", region);
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
                className="absolute inset-0 bg-black/80 backdrop-blur-sm"
                onClick={onClose}
            />

            {/* Modal */}
            <div className="relative w-full max-w-2xl bg-[#0e1117] border border-zinc-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">

                {/* Header */}
                <div className="p-6 border-b border-zinc-800 flex justify-between items-center bg-zinc-900/50">
                    <h2 className="text-xl font-bold text-white flex items-center gap-2">
                        <span className="text-2xl">⚙️</span> Settings
                    </h2>
                    <button onClick={onClose} className="text-zinc-400 hover:text-white transition">
                        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {/* Body */}
                <div className="flex flex-1 overflow-hidden">
                    {/* Sidebar Tabs */}
                    <div className="w-48 border-r border-zinc-800 bg-zinc-900/30 p-4 flex flex-col gap-2">
                        {[
                            { id: 'profile', label: 'Profile', icon: '👤' },
                            { id: 'preferences', label: 'Preferences', icon: '🌍' },
                            { id: 'api', label: 'Ai Keys', icon: '🔑' },
                            { id: 'feedback', label: 'Feedback', icon: '💬' },
                        ].map(tab => (
                            <button
                                key={tab.id}
                                onClick={() => { setActiveTab(tab.id); setMsg(null); }}
                                className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-bold transition-all ${activeTab === tab.id
                                    ? "bg-[var(--color-cta)] text-black shadow-[0_0_15px_rgba(34,211,238,0.3)]"
                                    : "text-zinc-400 hover:text-white hover:bg-white/5"
                                    }`}
                            >
                                <span>{tab.icon}</span> {tab.label}
                            </button>
                        ))}
                    </div>

                    {/* Content Area */}
                    <div className="flex-1 p-8 overflow-y-auto">

                        {/* Messages */}
                        {msg && (
                            <div className={`mb-6 p-4 rounded-xl border flex items-center gap-3 ${msg.type === 'success'
                                ? 'bg-green-500/10 border-green-500/30 text-green-400'
                                : 'bg-red-500/10 border-red-500/30 text-red-400'
                                }`}>
                                {msg.type === 'success' ? '✅' : '❌'} {msg.text}
                            </div>
                        )}

                        {/* PROFILE TAB */}
                        {activeTab === 'profile' && (
                            <div className="space-y-6">
                                <h3 className="text-lg font-bold text-white mb-4">User Profile</h3>

                                <div className="flex items-center gap-6 mb-8">
                                    <img
                                        src={user.picture}
                                        className="w-20 h-20 rounded-full border-2 border-[var(--color-cta)] shadow-[0_0_20px_rgba(34,211,238,0.2)]"
                                    />
                                    <div>
                                        <div className="text-xl font-bold text-white">{user.name}</div>
                                        <div className="text-sm text-zinc-500">{user.email}</div>
                                        {user.is_admin && (
                                            <span className="mt-2 inline-block px-2 py-0.5 rounded text-[10px] font-bold bg-purple-500/20 text-purple-400 border border-purple-500/30">
                                                GAME MASTER
                                            </span>
                                        )}
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <label className="text-xs font-bold text-zinc-400 uppercase tracking-wider">Display Nickname</label>
                                    <input
                                        type="text"
                                        value={nickname}
                                        onChange={(e) => setNickname(e.target.value)}
                                        className="w-full bg-black/40 border border-zinc-700 rounded-xl px-4 py-3 text-white focus:border-[var(--color-cta)] focus:ring-1 focus:ring-[var(--color-cta)] outline-none transition"
                                        placeholder="Enter your nickname"
                                    />
                                    <p className="text-xs text-zinc-600">This name will appear on the public leaderboards.</p>
                                </div>

                                <button
                                    onClick={handleSaveProfile}
                                    disabled={loading}
                                    className="px-6 py-3 bg-[var(--color-cta)] text-black font-bold rounded-xl hover:shadow-[0_0_20px_rgba(34,211,238,0.4)] transition disabled:opacity-50"
                                >
                                    {loading ? "Saving..." : "Save Profile"}
                                </button>
                            </div>
                        )}

                        {/* PREFERENCES TAB */}
                        {activeTab === 'preferences' && (
                            <div className="space-y-6">
                                <h3 className="text-lg font-bold text-white mb-4">App Preferences</h3>

                                <div className="space-y-2">
                                    <label className="text-xs font-bold text-zinc-400 uppercase tracking-wider">Region Format</label>
                                    <select
                                        className="w-full bg-[#1e293b] border border-[#334155] rounded-lg px-3 py-2 text-white focus:outline-none focus:border-[#00f2ea] opacity-50 cursor-not-allowed"
                                        value={region}
                                        disabled
                                    >
                                        <option value="TW">🇹🇼 Taiwan (TWD)</option>
                                    </select>
                                    <p className="text-xs text-gray-500 mt-1">Other regions coming in Q4 2026</p>
                                </div>

                                {user?.is_admin && (
                                    <div className="space-y-2">
                                        <label className="text-xs font-bold text-zinc-400 uppercase tracking-wider">GM Controls</label>
                                        <div className="flex items-center gap-3 p-3 bg-purple-500/10 border border-purple-500/30 rounded-xl">
                                            <div className="flex-1">
                                                <div className="font-bold text-white">Premium Status</div>
                                                <div className="text-xs text-zinc-400">Unlock advanced features for testing</div>
                                            </div>
                                            <button
                                                onClick={() => setIsPremium(!isPremium)}
                                                className={`w-12 h-6 rounded-full transition-colors relative ${isPremium ? 'bg-[var(--color-cta)]' : 'bg-zinc-700'
                                                    }`}
                                            >
                                                <div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-transform ${isPremium ? 'left-7' : 'left-1'
                                                    }`} />
                                            </button>
                                        </div>
                                    </div>
                                )}

                                <div className="space-y-2">
                                    <label className="text-xs font-bold text-zinc-400 uppercase tracking-wider">Language</label>
                                    <div className="grid grid-cols-2 gap-4">
                                        <button
                                            onClick={() => setLanguage('en')}
                                            className={`p-4 rounded-xl border flex flex-col items-center gap-2 transition ${language === 'en'
                                                ? 'bg-[var(--color-cta)]/10 border-[var(--color-cta)] text-white'
                                                : 'border-zinc-800 text-zinc-500 hover:border-zinc-600'
                                                }`}
                                        >
                                            <span className="text-2xl">🇺🇸</span>
                                            <span className="font-bold">English</span>
                                        </button>
                                        <button
                                            onClick={() => setLanguage('zh')}
                                            className={`p-4 rounded-xl border flex flex-col items-center gap-2 transition ${language === 'zh'
                                                ? 'bg-[var(--color-cta)]/10 border-[var(--color-cta)] text-white'
                                                : 'border-zinc-800 text-zinc-500 hover:border-zinc-600'
                                                }`}
                                        >
                                            <span className="text-2xl">🇹🇼</span>
                                            <span className="font-bold">繁體中文</span>
                                        </button>
                                        <button
                                            onClick={() => setLanguage('zh-CN')}
                                            className={`p-4 rounded-xl border flex flex-col items-center gap-2 transition ${language === 'zh-CN'
                                                ? 'bg-[var(--color-cta)]/10 border-[var(--color-cta)] text-white'
                                                : 'border-zinc-800 text-zinc-500 hover:border-zinc-600'
                                                }`}
                                        >
                                            <span className="text-2xl">🇨🇳</span>
                                            <span className="font-bold">簡體中文</span>
                                        </button>
                                    </div>
                                    <p className="text-xs text-yellow-500/80 mt-2">⚠️ Note: Language switching is deferred to Q2.</p>
                                </div>

                                <button
                                    onClick={handleSavePreferences}
                                    className="px-6 py-3 bg-zinc-800 text-white font-bold rounded-xl hover:bg-zinc-700 transition"
                                >
                                    Save Preferences
                                </button>
                            </div>
                        )}

                        {/* API KEY TAB */}
                        {activeTab === 'api' && (
                            <div className="space-y-6">
                                <h3 className="text-lg font-bold text-white mb-4">AI Integration</h3>

                                <div className="p-4 bg-teal-500/10 border border-teal-500/20 rounded-xl text-sm text-teal-400 mb-6">
                                    💡 <strong>Gemini Copilot</strong> requires a valid API Key.
                                    <br />The default key is provided by the system, but you can override it here for higher rate limits.
                                </div>

                                <div className="space-y-2">
                                    <label className="text-xs font-bold text-zinc-400 uppercase tracking-wider">Gemini API Key</label>
                                    <input
                                        type="password"
                                        value={apiKey}
                                        onChange={(e) => setApiKey(e.target.value)}
                                        className="w-full bg-black/40 border border-zinc-700 rounded-xl px-4 py-3 text-white focus:border-[var(--color-cta)] outline-none font-mono"
                                        placeholder="AIzaSy..."
                                    />
                                </div>

                                <button
                                    onClick={handleSaveKey}
                                    className="px-6 py-3 bg-zinc-800 text-white font-bold rounded-xl hover:bg-zinc-700 transition"
                                >
                                    Save Key
                                </button>
                            </div>
                        )}

                        {/* FEEDBACK TAB */}
                        {activeTab === 'feedback' && (
                            <div className="space-y-6">
                                <h3 className="text-lg font-bold text-white mb-4">Send Feedback</h3>
                                <p className="text-sm text-zinc-400">Help us improve the Martian System! Report bugs or suggest features.</p>

                                <div className="grid grid-cols-2 gap-4">
                                    <div className="space-y-2">
                                        <label className="text-xs font-bold text-zinc-400 uppercase tracking-wider">Type</label>
                                        <select
                                            value={feedbackType}
                                            onChange={(e) => setFeedbackType(e.target.value)}
                                            className="w-full bg-black/40 border border-zinc-700 rounded-xl px-4 py-3 text-white focus:border-[var(--color-cta)] outline-none"
                                        >
                                            <option value="suggestion">💡 Suggestion</option>
                                            <option value="bug">🐛 Bug Report</option>
                                            <option value="question">❓ Question</option>
                                        </select>
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-xs font-bold text-zinc-400 uppercase tracking-wider">Category</label>
                                        <select
                                            value={feedbackCategory}
                                            onChange={(e) => setFeedbackCategory(e.target.value)}
                                            className="w-full bg-black/40 border border-zinc-700 rounded-xl px-4 py-3 text-white focus:border-[var(--color-cta)] outline-none"
                                        >
                                            <option value="settings">Settings / General</option>
                                            <option value="mars_strategy">Mars Strategy</option>
                                            <option value="portfolio">Portfolio</option>
                                            <option value="bar_chart_race">Visualizations</option>
                                            <option value="ai_copilot">AI Copilot</option>
                                        </select>
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <label className="text-xs font-bold text-zinc-400 uppercase tracking-wider">Message</label>
                                    <textarea
                                        value={feedbackMessage}
                                        onChange={(e) => setFeedbackMessage(e.target.value)}
                                        className="w-full h-32 bg-black/40 border border-zinc-700 rounded-xl px-4 py-3 text-white focus:border-[var(--color-cta)] outline-none resize-none"
                                        placeholder="Describe your feedback here..."
                                    />
                                </div>

                                <button
                                    onClick={handleSendFeedback}
                                    disabled={loading}
                                    className="px-6 py-3 bg-[var(--color-cta)] text-black font-bold rounded-xl hover:shadow-[0_0_20px_rgba(34,211,238,0.4)] transition disabled:opacity-50"
                                >
                                    {loading ? "Sending..." : "Submit Feedback"}
                                </button>
                            </div>
                        )}

                    </div>
                </div>
            </div>
        </div>
    );
}
