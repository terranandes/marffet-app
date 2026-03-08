"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import toast from "react-hot-toast";
import { useLanguage } from "../lib/i18n/LanguageContext";
import { useUser } from "../lib/UserContext";

interface User {
    id: string | null;
    email?: string;
    name?: string;
    nickname?: string;
    picture?: string;
    is_admin?: boolean;
    is_premium?: boolean;
    tier?: string;
}

interface SettingsModalProps {
    isOpen: boolean;
    onClose: () => void;
    user: User | null;
    onUpdateUser: () => void; // Trigger parent re-fetch
    initialTab?: string;
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

export default function SettingsModal({ isOpen, onClose, user, onUpdateUser, initialTab = "profile" }: SettingsModalProps) {
    const [activeTab, setActiveTab] = useState(initialTab); // profile, preferences, api, sponsor, help

    // Form States
    const [nickname, setNickname] = useState(user?.nickname || "");
    const [apiKey, setApiKey] = useState("");
    const { language, setLanguage, t } = useLanguage();
    const [region, setRegion] = useState("TW"); // Fixed to TW
    const [defaultPage, setDefaultPage] = useState("/"); // Default to Dashboard
    const [isPremium, setIsPremium] = useState(false);

    const { login, logout } = useUser();

    // Feedback State
    const [feedbackCategory, setFeedbackCategory] = useState("settings");
    const [feedbackType, setFeedbackType] = useState("suggestion");
    const [feedbackMessage, setFeedbackMessage] = useState("");

    // Read initial internal state from props if we need to force it open
    // This allows the layout to control it directly or we use custom events
    const [isInternalOpen, setIsInternalOpen] = useState(isOpen);

    useEffect(() => {
        setIsInternalOpen(isOpen);
    }, [isOpen]);

    // Global event listener for mobile bottom bar
    useEffect(() => {
        const handleOpenSettings = () => {
            setIsInternalOpen(true);
            setActiveTab("profile");
        };
        window.addEventListener('open-mobile-settings', handleOpenSettings);
        return () => window.removeEventListener('open-mobile-settings', handleOpenSettings);
    }, []);

    // When internal close happens, call the prop onClose too
    const handleClose = () => {
        setIsInternalOpen(false);
        onClose();
    };

    // Status
    const [loading, setLoading] = useState(false);
    const [syncLoading, setSyncLoading] = useState(false);
    const [msg, setMsg] = useState<{ type: 'success' | 'error', text: string } | null>(null);
    const [showDocModal, setShowDocModal] = useState(false); // Documentation Modal State

    // Initialize from LocalStorage & User Props
    useEffect(() => {
        if (isOpen) {
            setNickname(user?.nickname || "");
            setApiKey(localStorage.getItem("marffet_api_key") || "");
            setRegion(localStorage.getItem("marffet_region") || "TW");
            setDefaultPage(localStorage.getItem("marffet_default_page") || "/");
            setIsPremium(localStorage.getItem("marffet_premium") === "true");
            setActiveTab(initialTab);
            setMsg(null);
        }
    }, [isOpen, user, initialTab]);

    const handleSaveProfile = async () => {
        setLoading(true);
        setMsg(null);
        try {
            const API_URL = "";
            const res = await fetch(`${API_URL}/api/auth/profile`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ nickname }),
                credentials: "include"
            });

            if (res.ok) {
                toast.success("Profile updated successfully");
                onUpdateUser(); // Refresh parent user state
            } else {
                toast.error("Failed to update profile");
            }
        } catch (e) {
            toast.error("Network error");
        }
        setLoading(false);
    };

    const handleSyncStats = async () => {
        setSyncLoading(true);
        setMsg(null);
        try {
            const API_URL = "";
            const res = await fetch(`${API_URL}/api/portfolio/sync-stats`, {
                method: "POST",
                credentials: "include"
            });
            if (res.ok) {
                const data = await res.json();
                toast.success(`Rank Synced! ROI: ${data.roi}%`);
            } else {
                toast.error("Sync failed");
            }
        } catch (e) {
            toast.error("Network error");
        }
        setSyncLoading(false);
    };

    const handleSavePreferences = () => {
        localStorage.setItem("marffet_region", region);
        localStorage.setItem("marffet_default_page", defaultPage);
        localStorage.setItem("marffet_premium", String(isPremium));
        toast.success(t('Settings.SavePreferences') + " (reload to apply)");
    };

    const handleSaveKey = () => {
        localStorage.setItem("marffet_api_key", apiKey);
        toast.success("API Key saved securely");
    };

    const handleSendFeedback = async () => {
        if (!feedbackMessage.trim()) {
            toast.error("Please enter a message");
            return;
        }
        setLoading(true);
        try {
            const API_URL = "";
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
                toast.success("Feedback sent! We appreciate it.");
                setFeedbackMessage("");
            } else {
                toast.error("Failed to send feedback");
            }
        } catch (e) {
            toast.error("Network error");
        }
        setLoading(false);
    };

    if (!isInternalOpen) return null;

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/80 backdrop-blur-md"
                onClick={handleClose}
            />

            {/* Modal */}
            <div className="relative w-full max-w-2xl bg-black/60 backdrop-blur-2xl border border-white/10 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">

                {/* Header */}
                <div className="p-6 border-b border-white/10 flex justify-between items-center bg-white/5">
                    <h2 className="text-xl font-bold text-white flex items-center gap-2">
                        <span className="text-2xl">⚙️</span> {t('Settings.Title') || "Settings"}
                    </h2>
                    <button onClick={handleClose} className="text-zinc-400 hover:text-white transition hover:rotate-90 duration-300">
                        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {/* Body */}
                <div className="flex flex-col md:flex-row flex-1 overflow-hidden">
                    {/* Sidebar Tabs */}
                    <div className="w-full md:w-52 border-b md:border-b-0 md:border-r border-white/10 bg-black/20 p-4 flex flex-row md:flex-col gap-2 overflow-x-auto md:overflow-visible shrink-0">
                        {[
                            { id: 'profile', label: t('Settings.ProfileTab') || 'Profile', icon: '👤' },
                            { id: 'preferences', label: t('Settings.PreferencesTab') || 'Preferences', icon: '🌍' },
                            { id: 'api', label: t('Settings.ApiTab') || 'Ai Keys', icon: '🔑' },
                            { id: 'sponsor', label: t('Settings.SponsorTab') || 'Sponsor Us', icon: '☕' },
                            { id: 'help', label: t('Settings.HelpTab') || 'Help', icon: '📚' },
                            { id: 'support', label: t('Settings.SupportTab') || 'Support', icon: '💬' },
                        ].map(tab => (
                            <button
                                key={tab.id}
                                onClick={() => { setActiveTab(tab.id); setMsg(null); }}
                                className={`flex items-center gap-3 px-4 py-3 text-sm font-bold transition-colors relative ${activeTab === tab.id
                                    ? "text-cyan-400"
                                    : "text-zinc-400 hover:text-white hover:bg-white/5 rounded-xl"
                                    }`}
                            >
                                <span className="relative z-10">{tab.icon}</span>
                                <span className="relative z-10">{tab.label}</span>
                                {activeTab === tab.id && (
                                    <motion.div
                                        layoutId="activeSettingsTab"
                                        className="absolute inset-0 bg-cyan-500/10 border border-cyan-500/50 rounded-xl shadow-[0_0_15px_rgba(34,211,238,0.2)]"
                                        transition={{ type: "spring", stiffness: 400, damping: 30 }}
                                    />
                                )}
                            </button>
                        ))}
                    </div>

                    {/* Content Area */}
                    <div className="flex-1 p-8 overflow-y-auto bg-transparent relative">

                        {/* Messages are now shown via react-hot-toast */}

                        {/* PROFILE TAB */}
                        <AnimatePresence mode="wait">
                            {activeTab === 'profile' && (
                                <motion.div key="profile" initial={{ opacity: 0, x: 12 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -12 }} transition={{ duration: 0.2 }} className="space-y-8">
                                    <h3 className="text-lg font-bold text-white mb-4 border-b border-white/10 pb-2">{t('Settings.UserProfile') || "User Profile"}</h3>

                                    {user ? (
                                        <>
                                            <div className="flex gap-4">
                                                <div className="relative">
                                                    <img
                                                        src={user.picture || ""}
                                                        alt="Profile"
                                                        className="w-20 h-20 rounded-xl object-cover border border-zinc-700 shadow-xl"
                                                    />
                                                    {user.is_admin && <div className="absolute -bottom-2 -right-2 text-xl">👑</div>}
                                                </div>
                                                <div className="flex flex-col justify-center">
                                                    <div className="text-2xl font-bold text-white">{user.name}</div>
                                                    <div className="text-sm text-zinc-500 font-mono">{user.email}</div>
                                                    {user.is_admin && (
                                                        <div className="mt-1 text-xs text-amber-500 font-bold bg-amber-500/10 inline-block px-2 py-0.5 rounded border border-amber-500/20">
                                                            SYSTEM ADMINISTRATOR
                                                        </div>
                                                    )}
                                                </div>
                                            </div>

                                            <div className="space-y-6 pt-2">
                                                <div className="space-y-2">
                                                    <label className="text-xs font-bold text-cyan-400 uppercase tracking-wider">{t('Settings.DisplayNickname') || "Display Nickname"}</label>
                                                    <div className="flex gap-2">
                                                        <input
                                                            type="text"
                                                            value={nickname}
                                                            onChange={(e) => setNickname(e.target.value)}
                                                            className="flex-1 bg-black/40 border border-zinc-700 rounded-xl px-4 py-3 text-white focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 outline-none transition"
                                                            placeholder={t('Settings.EnterNickname') || "Enter your nickname"}
                                                        />
                                                        <button
                                                            onClick={handleSaveProfile}
                                                            disabled={loading}
                                                            className="px-6 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 text-white font-bold rounded-xl hover:shadow-[0_0_20px_rgba(34,211,238,0.4)] transition disabled:opacity-50"
                                                        >
                                                            {loading ? "..." : (t('Settings.Save') || "Save")}
                                                        </button>
                                                    </div>
                                                    <p className="text-xs text-zinc-600">{t('Settings.VisibleOnLeaderboards') || "Visible on public leaderboards."}</p>
                                                </div>

                                                {/* Leaderboard Rank Section */}
                                                <div className="pt-6 border-t border-white/10">
                                                    <label className="text-xs font-bold text-yellow-500 uppercase tracking-wider mb-2 block">{t('Settings.LeaderboardRank') || "🏆 Leaderboard Rank"}</label>
                                                    <div className="flex justify-between items-center p-4 rounded-xl bg-yellow-500/5 border border-yellow-500/20">
                                                        <p className="text-xs text-gray-400">{t('Settings.UpdateWealthStats') || "Update your wealth stats on the global leaderboard."}</p>
                                                        <button
                                                            onClick={handleSyncStats}
                                                            disabled={syncLoading}
                                                            className="bg-yellow-500/20 text-yellow-400 hover:bg-yellow-500/40 px-4 py-2 rounded-lg text-sm font-bold border border-yellow-500/50 transition hover:shadow-[0_0_15px_rgba(234,179,8,0.3)] disabled:opacity-50 shrink-0 ml-4"
                                                        >
                                                            {syncLoading ? (t('Settings.Syncing') || "Syncing...") : (t('Settings.SyncNow') || "Sync Now")}
                                                        </button>
                                                    </div>
                                                </div>

                                                {/* Sign Out Button */}
                                                <div className="pt-6 border-t border-white/10">
                                                    <button
                                                        onClick={() => logout()}
                                                        className="w-full py-3 bg-red-500/10 hover:bg-red-500/20 text-red-500 font-bold rounded-xl transition border border-red-500/20 shadow-[0_0_15px_rgba(239,68,68,0.1)] flex items-center justify-center gap-2"
                                                    >
                                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                                                        </svg>
                                                        {t('Sidebar.SignOut') || "Sign Out"}
                                                    </button>
                                                </div>
                                            </div>
                                        </>
                                    ) : (
                                        <div className="flex flex-col items-center justify-center py-10 space-y-6">
                                            <div className="w-24 h-24 rounded-full bg-zinc-800 flex items-center justify-center border-4 border-zinc-700 shadow-inner">
                                                <span className="text-zinc-500 text-4xl">👤</span>
                                            </div>
                                            <div className="text-center space-y-2">
                                                <h4 className="text-xl font-bold text-white">Welcome Guest</h4>
                                                <p className="text-sm text-zinc-400 max-w-xs mx-auto">
                                                    Sign in to save your portfolio, track your investments across devices, and compete on the leaderboard.
                                                </p>
                                            </div>

                                            <div className="w-full max-w-sm pt-4">
                                                <button
                                                    onClick={() => login()}
                                                    className="flex items-center justify-center gap-3 w-full py-4 bg-white text-black font-bold rounded-xl hover:bg-zinc-200 transition-all shadow-lg hover:shadow-xl"
                                                >
                                                    <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
                                                        <path d="M12.545,10.239v3.821h5.445c-0.712,2.315-2.647,3.972-5.445,3.972c-3.332,0-6.033-2.701-6.033-6.032s2.701-6.032,6.033-6.032c1.498,0,2.866,0.549,3.921,1.453l2.814-2.814C17.503,2.988,15.139,2,12.545,2C7.021,2,2.543,6.477,2.543,12s4.478,10,10.002,10c8.396,0,10.249-7.85,9.426-11.748L12.545,10.239z" />
                                                    </svg>
                                                    {t('Sidebar.SignInGoogle') || "Sign in with Google"}
                                                </button>
                                            </div>
                                        </div>
                                    )}
                                </motion.div>
                            )}

                            {/* PREFERENCES TAB */}
                            {activeTab === 'preferences' && (
                                <motion.div key="preferences" initial={{ opacity: 0, x: 12 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -12 }} transition={{ duration: 0.2 }} className="space-y-8">
                                    <h3 className="text-lg font-bold text-white mb-4 border-b border-white/10 pb-2">{t('Settings.AppPreferences') || "App Preferences"}</h3>

                                    {/* Start Page Selector */}
                                    <div className="space-y-2">
                                        <label className="text-xs font-bold text-cyan-400 uppercase tracking-wider">{t('Settings.StartPage') || "Start Page"}</label>
                                        <select
                                            className="w-full bg-black/40 border border-zinc-700 rounded-xl px-4 py-3 text-white focus:border-cyan-500 outline-none"
                                            value={defaultPage}
                                            onChange={(e) => setDefaultPage(e.target.value)}
                                        >
                                            <option value="/">🏠 {t('Home.Title') || 'Home'}</option>
                                            <option value="/mars">🚀 {t('Sidebar.MarsStrategy')}</option>
                                            <option value="/portfolio">📊 {t('Sidebar.Portfolio')}</option>
                                            <option value="/trend">📈 {t('Sidebar.TrendDashboard')}</option>
                                            <option value="/viz">📉 {t('Sidebar.Visualizations')}</option>
                                            <option value="/cb">💹 {t('Sidebar.ConvertibleBond')}</option>
                                            <option value="/myrace">🏁 {t('Sidebar.MyPortfolioRace') || 'My Race'}</option>
                                        </select>
                                        <p className="text-xs text-zinc-600">{t('Settings.LoadsAutomatically') || "Loads automatically on visit."}</p>
                                    </div>

                                    {/* Language Selector */}
                                    <div className="space-y-2">
                                        <label className="text-xs font-bold text-cyan-400 uppercase tracking-wider">{t('Settings.Language')}</label>
                                        <div className="grid grid-cols-1 gap-2">
                                            {[
                                                { code: 'en', flag: '🇺🇸', label: 'English' },
                                                { code: 'zh-TW', flag: '🇹🇼', label: '繁體中文' },
                                                { code: 'zh-CN', flag: '🇨🇳', label: '简体中文' }
                                            ].map(langOption => (
                                                <button
                                                    key={langOption.code}
                                                    onClick={() => setLanguage(langOption.code as any)}
                                                    className={`p-3 rounded-xl flex items-center justify-between text-left transition-all border ${language === langOption.code
                                                        ? 'bg-cyan-900/20 border-cyan-500/50'
                                                        : 'bg-zinc-800/20 border-zinc-800 hover:border-cyan-500/30'
                                                        }`}
                                                >
                                                    <div className="flex items-center gap-3">
                                                        <span className="text-2xl">{langOption.flag}</span>
                                                        <div className={`font-bold ${language === langOption.code ? 'text-white' : 'text-gray-400'}`}>
                                                            {langOption.label}
                                                        </div>
                                                    </div>
                                                    {language === langOption.code && (
                                                        <div className="text-cyan-400 text-xs font-bold px-2 py-1 bg-cyan-900/50 rounded border border-cyan-500/30">
                                                            Active
                                                        </div>
                                                    )}
                                                </button>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Region Selector (Fixed) */}
                                    <div className="space-y-2">
                                        <label className="text-xs font-bold text-cyan-400 uppercase tracking-wider">{t('Settings.RegionFormat') || "Region Format"}</label>
                                        <div className="grid grid-cols-1 gap-2">
                                            <div className="p-3 bg-cyan-900/20 border border-cyan-500/50 rounded-xl flex items-center justify-between">
                                                <div className="flex items-center gap-3">
                                                    <span className="text-2xl">🇹🇼</span>
                                                    <div className="font-bold text-white">{t('Settings.Taiwan') || "Taiwan (TWD)"}</div>
                                                </div>
                                                <div className="text-cyan-400 text-xs font-bold px-2 py-1 bg-cyan-900/50 rounded border border-cyan-500/30">{t('Settings.Active') || "Active"}</div>
                                            </div>
                                            <div className="p-3 bg-zinc-800/20 border border-zinc-800 rounded-xl flex items-center justify-between opacity-50 cursor-not-allowed">
                                                <div className="flex items-center gap-3">
                                                    <span className="text-2xl">🇨🇳</span>
                                                    <div className="font-bold text-gray-500">{t('Settings.China') || "China"}</div>
                                                </div>
                                            </div>
                                            <div className="p-3 bg-zinc-800/20 border border-zinc-800 rounded-xl flex items-center justify-between opacity-50 cursor-not-allowed">
                                                <div className="flex items-center gap-3">
                                                    <span className="text-2xl">🇺🇸</span>
                                                    <div className="font-bold text-gray-500">{t('Settings.USA') || "USA"}</div>
                                                </div>
                                            </div>
                                        </div>
                                        <p className="text-xs text-zinc-600 mt-1">{t('Settings.RegionComingSoon') || "Global regions coming in Q4 2026."}</p>
                                    </div>

                                    {/* Premium Badge (Server-granted, non-admin) */}
                                    {user?.is_premium && !user?.is_admin && (
                                        <div className="space-y-2">
                                            <label className="text-xs font-bold text-yellow-400 uppercase tracking-wider">{t('Settings.AccountStatus') || "Account Status"}</label>
                                            <div className="flex items-center gap-3 p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-xl">
                                                <div className="flex-1">
                                                    <div className="font-bold text-white flex items-center gap-2">⭐ {t('Settings.PremiumActive') || "Premium Active"}</div>
                                                    <div className="text-xs text-zinc-400">{t('Settings.PremiumDesc') || "Privileged account — all premium features unlocked"}</div>
                                                </div>
                                                <div className="px-3 py-1 rounded-full text-[10px] uppercase tracking-wider font-bold bg-yellow-500/20 text-yellow-400 border border-yellow-500/30">
                                                    {t('Settings.Active') || "Active"}
                                                </div>
                                            </div>
                                        </div>
                                    )}

                                    {/* GM Controls (Admin-only toggle for testing) */}
                                    {user?.is_admin && (
                                        <div className="space-y-2">
                                            <label className="text-xs font-bold text-amber-400 uppercase tracking-wider">GM Controls</label>
                                            <div className="flex items-center gap-3 p-3 bg-amber-900/10 border border-amber-500/30 rounded-xl">
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
                                        {t('Settings.SavePreferences') || "Save Preferences"}
                                    </button>
                                </motion.div>
                            )}

                            {/* API KEY TAB */}
                            {activeTab === 'api' && (
                                <motion.div key="api" initial={{ opacity: 0, x: 12 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -12 }} transition={{ duration: 0.2 }} className="space-y-8">
                                    <h3 className="text-lg font-bold text-white mb-4 border-b border-white/10 pb-2">{t('Settings.AIIntegration') || "AI Integration"}</h3>

                                    <div className="p-4 bg-teal-500/10 border border-teal-500/20 rounded-xl text-sm text-teal-200 mb-6">
                                        💡 <strong>{t('Settings.GeminiCopilot') || "Gemini Copilot"}</strong> {t('Settings.RequiresAPIKey') || "requires a valid API Key."}
                                        <br /><span className="text-teal-400/70 text-xs">{t('Settings.DefaultKeyDesc') || "The default key is provided by the system, but you can override it here for higher rate limits."}</span>
                                    </div>

                                    <div className="space-y-2">
                                        <label className="text-xs font-bold text-cyan-400 uppercase tracking-wider">{t('Settings.GeminiAPIKey') || "Gemini API Key"}</label>
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
                                        {t('Settings.SaveKey') || "Save Key"}
                                    </button>
                                </motion.div>
                            )}

                            {/* HELP TAB */}
                            {activeTab === 'help' && (
                                <motion.div key="help" initial={{ opacity: 0, x: 12 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -12 }} transition={{ duration: 0.2 }} className="space-y-6">
                                    <h3 className="text-lg font-bold text-white mb-4 border-b border-white/10 pb-2">{t('Settings.HelpCenter') || "Help Center"}</h3>

                                    <div className="mb-6">
                                        <button onClick={() => setShowDocModal(true)}
                                            className="p-4 w-full bg-zinc-800/50 hover:bg-zinc-800 border border-zinc-700 rounded-xl transition group flex items-center gap-4 text-left">
                                            <div className="text-2xl">📚</div>
                                            <div>
                                                <div className="font-bold text-white group-hover:text-cyan-400 transition">{t('Settings.Documentation') || "Documentation"}</div>
                                                <div className="text-xs text-zinc-500">{t('Settings.DocDesc') || "Visit our Wiki for detailed guides"}</div>
                                            </div>
                                        </button>
                                    </div>

                                    <Accordion title={<span className="text-cyan-400 flex items-center gap-2">📖 {t('Settings.FeatureGuide') || "Feature Guide"}</span>} defaultOpen={false}>
                                        <div><strong className="text-cyan-300">{t('Sidebar.MarsStrategy')}:</strong> {t('Settings.MarsDesc') || "Search & filter stocks using Top 50 strategy"}</div>
                                        <div><strong className="text-cyan-300">{t('Sidebar.Race')}:</strong> {t('Settings.RaceDesc') || "Animated wealth growth visualization"}</div>
                                        <div><strong className="text-cyan-300">{t('Sidebar.Portfolio')}:</strong> {t('Settings.PortfolioDesc') || "Track real investments with groups & transactions"}</div>
                                        <div><strong className="text-cyan-300">{t('Sidebar.Trend')}:</strong> {t('Settings.TrendDesc') || "Monthly cost trends and live prices"}</div>
                                        <div><strong className="text-cyan-300">{t('Sidebar.MyRace')}:</strong> {t('Settings.MyRaceDesc') || "Watch your portfolio stocks compete"}</div>
                                        <div><strong className="text-cyan-300">{t('AICopilot.Title') || "Mars AI Copilot"}:</strong> {t('Settings.CopilotDesc') || "Get investment advice from Mars AI"}</div>
                                        <div><strong className="text-cyan-300">{t('Settings.Leaderboard') || "Leaderboard"}:</strong> {t('Settings.LeaderboardDesc') || "Community rankings & public profiles"}</div>
                                    </Accordion>

                                    <Accordion title={<span className="text-yellow-400 flex items-center gap-2">⭐ {t('Settings.PremiumFeatures') || "Premium Features"}</span>}>
                                        <div>• <strong>{t('Settings.AIPersonality') || "AI Personality"}:</strong> {t('Settings.RuthlessMode') || "Ruthless Wealth Manager mode"}</div>
                                        <div>• <strong>{t('Settings.PortfolioGroups') || "Portfolio Groups"}:</strong> {t('Settings.GroupsLimit') || "Up to 30 (vs 11 free)"}</div>
                                        <div>• <strong>{t('Settings.TargetsGroup') || "Targets/Group"}:</strong> {t('Settings.TargetsLimit') || "Up to 200 (vs 50 free)"}</div>
                                        <div>• <strong>{t('Settings.Transactions') || "Transactions"}:</strong> {t('Settings.TxLimit') || "Up to 1000 (vs 100 free)"}</div>
                                        <div>• <strong>{t('Settings.CBNotifications') || "CB Notifications"}:</strong> {t('Settings.EmailAlerts') || "Email alerts"}</div>
                                        <div>• <strong>{t('Settings.DataExport') || "Data Export"}:</strong> {t('Settings.FilteredExcel') || "Filtered Excel"}</div>
                                    </Accordion>

                                    <div className="text-xs text-gray-500 italic text-center">
                                        💳 {t('Settings.SubscribeComingSoon') || "How to Subscribe: Coming Soon"}
                                    </div>
                                </motion.div>
                            )}

                            {/* SUPPORT TAB */}
                            {activeTab === 'support' && (
                                <motion.div key="support" initial={{ opacity: 0, x: 12 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -12 }} transition={{ duration: 0.2 }} className="space-y-6">
                                    <h3 className="text-lg font-bold text-white mb-4 border-b border-white/10 pb-2">{t('Settings.SupportTitle') || "Support & Feedback"}</h3>

                                    <div className="mb-6">
                                        <a href="mailto:support@marffet.com" className="p-4 bg-zinc-800/50 hover:bg-zinc-800 border border-zinc-700 rounded-xl transition group flex items-center gap-4">
                                            <div className="text-2xl">🆘</div>
                                            <div>
                                                <div className="font-bold text-white group-hover:text-cyan-400 transition">{t('Settings.EmailSupport') || "Email Support"}</div>
                                                <div className="text-xs text-zinc-500">{t('Settings.EmailSupportDesc') || "Get help directly from our team"}</div>
                                            </div>
                                        </a>
                                    </div>

                                    <div className="border-t border-white/10 pt-6">
                                        <h3 className="text-md font-bold text-white mb-4">{t('Settings.SendFeedback') || "Send Feedback"}</h3>
                                        <p className="text-sm text-zinc-400 mb-4">{t('Settings.FeedbackDesc') || "Help us improve the Marffet System! Report bugs or suggest features."}</p>

                                        <div className="grid grid-cols-2 gap-4 mb-4">
                                            <div className="space-y-2">
                                                <label className="text-xs font-bold text-cyan-400 uppercase tracking-wider">{t('Settings.Type') || "Type"}</label>
                                                <select
                                                    value={feedbackType}
                                                    onChange={(e) => setFeedbackType(e.target.value)}
                                                    className="w-full bg-black/40 border border-zinc-700 rounded-xl px-4 py-3 text-white focus:border-cyan-500 outline-none"
                                                >
                                                    <option value="suggestion">💡 {t('Settings.Suggestion') || "Suggestion"}</option>
                                                    <option value="bug">🐛 {t('Settings.BugReport') || "Bug Report"}</option>
                                                    <option value="question">❓ {t('Settings.Question') || "Question"}</option>
                                                </select>
                                            </div>
                                            <div className="space-y-2">
                                                <label className="text-xs font-bold text-cyan-400 uppercase tracking-wider">{t('Settings.Category') || "Category"}</label>
                                                <select
                                                    value={feedbackCategory}
                                                    onChange={(e) => setFeedbackCategory(e.target.value)}
                                                    className="w-full bg-black/40 border border-zinc-700 rounded-xl px-4 py-3 text-white focus:border-cyan-500 outline-none"
                                                >
                                                    <option value="settings">{t('Settings.SettingsGeneral') || "Settings / General"}</option>
                                                    <option value="subscription">{t('Settings.SubscriptionCat') || "Subscription"}</option>
                                                    <option value="mars_strategy">{t('Sidebar.MarsStrategy') || "Mars Strategy"}</option>
                                                    <option value="bar_chart_race">{t('Sidebar.Race') || "Bar Chart Race"}</option>
                                                    <option value="portfolio">{t('Sidebar.Portfolio') || "Portfolio"}</option>
                                                    <option value="trend">{t('Sidebar.Trend') || "Trend Dashboard"}</option>
                                                    <option value="my_race">{t('Sidebar.MyRace') || "My Portfolio Race"}</option>
                                                    <option value="ai_copilot">{t('AICopilot.Title') || "AI Copilot"}</option>
                                                    <option value="leaderboard">{t('Settings.Leaderboard') || "Leaderboard"}</option>
                                                    <option value="cash_ladder">{t('Sidebar.Ladder') || "Cash Ladder"}</option>
                                                    <option value="compound_interest">{t('Sidebar.Compound') || "Compound Interest"}</option>
                                                    <option value="other">{t('Settings.Other') || "Other"}</option>
                                                </select>
                                            </div>
                                        </div>

                                        <div className="space-y-2 mb-4">
                                            <label className="text-xs font-bold text-cyan-400 uppercase tracking-wider">{t('Settings.Message') || "Message"}</label>
                                            <textarea
                                                value={feedbackMessage}
                                                onChange={(e) => setFeedbackMessage(e.target.value)}
                                                className="w-full h-32 bg-black/40 border border-zinc-700 rounded-xl px-4 py-3 text-white focus:border-cyan-500 outline-none resize-none"
                                                placeholder={t('Settings.FeedbackPlaceholder') || "Describe your feedback here..."}
                                            />
                                        </div>

                                        <button
                                            onClick={handleSendFeedback}
                                            disabled={loading}
                                            className="w-full px-6 py-3 bg-gradient-to-r from-cyan-600 to-blue-600 text-white font-bold rounded-xl hover:shadow-[0_0_20px_rgba(34,211,238,0.4)] transition disabled:opacity-50"
                                        >
                                            {loading ? (t('Settings.Sending') || "Sending...") : (t('Settings.SubmitFeedback') || "Submit Feedback")}
                                        </button>
                                    </div>
                                </motion.div>
                            )}

                            {/* SPONSOR TAB */}
                            {activeTab === 'sponsor' && (
                                <motion.div key="sponsor" initial={{ opacity: 0, x: 12 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -12 }} transition={{ duration: 0.2 }} className="space-y-6">
                                    <h3 className="text-lg font-bold text-white mb-4 border-b border-white/10 pb-2">{t('Settings.SponsorTitle') || "Sponsor Us"}</h3>

                                    <div className="bg-gradient-to-br from-[#0e1117] to-zinc-900 border border-zinc-800 rounded-xl p-6 shadow-xl mb-6 relative overflow-hidden group">
                                        {/* Gradient overlay */}
                                        <div className="absolute inset-0 bg-gradient-to-r from-pink-500/10 via-purple-500/10 to-orange-500/10 opacity-50 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />

                                        <div className="relative z-10 space-y-4">
                                            <p className="text-zinc-300 text-sm leading-relaxed mb-6">
                                                {t('Settings.SponsorDesc') || "Sponsor to our membership via the links below to receive VIP and PREMIUM access in our app. We will manually inject the membership to your account."}
                                            </p>

                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                <a
                                                    href="https://ko-fi.com/terranandes"
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="flex items-center justify-center transition-all transform hover:-translate-y-1 hover:shadow-[0_0_20px_rgba(41,171,224,0.3)] rounded-xl"
                                                >
                                                    <img src="/images/kofi-blue-button.png" alt="Ko-fi" className="h-12 w-auto object-contain rounded-xl" />
                                                </a>

                                                <a
                                                    href="https://buymeacoffee.com/terranandes"
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="flex items-center justify-center transition-all transform hover:-translate-y-1 hover:shadow-[0_0_20px_rgba(255,221,0,0.3)] rounded-xl"
                                                >
                                                    <img src="/images/bmc-yellow-button.png" alt="Buy Me A Coffee" className="h-12 w-auto object-contain rounded-xl" />
                                                </a>
                                            </div>
                                        </div>
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>

                    </div>
                </div>
            </div>

            {/* Documentation Modal Overlay */}
            {showDocModal && (
                <div className="fixed inset-0 z-[110] flex items-center justify-center p-4 bg-black/90 backdrop-blur-md" onClick={() => setShowDocModal(false)}>
                    <div className="w-full max-w-3xl bg-[#0e1117] border border-cyan-500/30 rounded-2xl shadow-2xl h-[80vh] flex flex-col" onClick={e => e.stopPropagation()}>
                        <div className="p-6 border-b border-white/10 flex justify-between items-center bg-zinc-900/50">
                            <h2 className="text-xl font-bold text-white">📚 Documentation</h2>
                            <button onClick={() => setShowDocModal(false)} className="text-zinc-400 hover:text-white transition">✕</button>
                        </div>
                        <div className="flex-1 p-8 overflow-y-auto prose prose-invert max-w-none">
                            <h1>👽 Marffet Investment System</h1>
                            <p><strong>Project Marffet</strong> (Martian + Buffet) is a high-performance investment simulation and tracking tool designed to prove the "Top 50 Past Performers" strategy.</p>

                            <h2>🌟 Key Features</h2>

                            <h3>1. Mars Strategy Simulator</h3>
                            <ul>
                                <li><strong>The Philosophy</strong>: History repeats itself. Buying the top 50 winners of the past decade and holding them yields superior returns.</li>
                                <li><strong>The Tool</strong>: Real-time simulation of 20+ years of Taiwan Network History. Customizable Start Year, Principal, and Monthly Contribution.</li>
                            </ul>

                            <h3>2. Bar Chart Race</h3>
                            <ul>
                                <li><strong>Visual Proof</strong>: Watch a dynamic "Race" of stock assets over time. See how "Boring" stocks compound into massive wealth.</li>
                            </ul>

                            <h3>3. Portfolio Tracker & Leaderboard</h3>
                            <ul>
                                <li><strong>Track Your Journey</strong>: Input your own holdings and create groups (Dividend, Growth, Speculative).</li>
                                <li><strong>Sync Stats</strong>: Compare your ROI against the Global Leaderboard with a single click.</li>
                                <li><strong>Community</strong>: Compete with other users for the top spot.</li>
                            </ul>

                            <h3>4. AI Copilot</h3>
                            <ul>
                                <li><strong>Smart Analysis</strong>: Get investment advice and market insights from the Mars AI.</li>
                                <li><strong>Personalized</strong>: Tailored feedback based on your portfolio.</li>
                            </ul>

                            <h2>🚀 Getting Started</h2>
                            <h3>Access the App</h3>
                            <p>Sign in securely with your <strong>Google Account</strong> to access your personalized portfolio.</p>
                            <ul>
                                <li><strong>Guest Mode</strong>: Explore the system features without an account.</li>
                            </ul>

                            <h3>First Steps</h3>
                            <ol>
                                <li><strong>Login</strong>: Use your Google Account.</li>
                                <li><strong>Explore</strong>: Go to "Mars Strategy" to see the backtest results.</li>
                                <li><strong>Settings</strong>: Customize your profile, nickname, and default landing page.</li>
                            </ol>

                            <hr className="my-8 border-white/10" />
                            <p className="text-sm text-zinc-500 italic">*Built with ❤️ by the Marffet AI Team.*</p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
