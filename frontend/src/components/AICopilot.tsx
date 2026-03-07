import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";
import { useLanguage } from "@/lib/i18n/LanguageContext";

interface Message {
    role: "user" | "model";
    text: string;
    timestamp: number;
}

interface AICopilotProps {
    user: any;
    portfolioContext?: string;
}

const API_BASE = "";

// Sleek AI Icon SVG
const SparklesIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6 shrink-0">
        <path fillRule="evenodd" d="M9.315 7.584C12.195 3.883 16.695 1.5 21.75 1.5a.75.75 0 0 1 .75.75c0 5.056-2.383 9.555-6.084 12.436V15.75a.75.75 0 0 1-.75.75H14.61c-2.88 3.701-7.38 6.084-12.435 6.084a.75.75 0 0 1-.75-.75v-1.065c3.701-2.88 6.084-7.38 6.084-12.435h1.065A.75.75 0 0 1 9.315 7.584ZM12.75 12a.75.75 0 0 1 .75-.75h2.152a10.493 10.493 0 0 0 5.59-3.929 10.493 10.493 0 0 0-3.929 5.59v2.152a.75.75 0 0 1-.75.75H14.41a10.493 10.493 0 0 0-5.59 3.929A10.492 10.492 0 0 0 12.75 12Z" clipRule="evenodd" />
    </svg>
);

const LockIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
        <path fillRule="evenodd" d="M12 1.5a5.25 5.25 0 0 0-5.25 5.25v3a3 3 0 0 0-3 3v6.75a3 3 0 0 0 3 3h10.5a3 3 0 0 0 3-3v-6.75a3 3 0 0 0-3-3v-3c0-2.9-2.35-5.25-5.25-5.25Zm3.75 8.25v-3a3.75 3.75 0 1 0-7.5 0v3h7.5Z" clipRule="evenodd" />
    </svg>
);

// Loading Animation component
const ThinkingIndicator = () => (
    <div className="flex justify-start my-2">
        <div className="bg-[#1e1e24]/80 border border-white/10 px-4 py-3 rounded-2xl rounded-tl-sm flex gap-1 items-center shadow-lg backdrop-blur-md">
            <motion.div
                className="w-1.5 h-1.5 bg-pink-400 rounded-full"
                animate={{ y: [0, -4, 0] }} transition={{ repeat: Infinity, duration: 0.6, ease: "easeInOut", delay: 0 }}
            />
            <motion.div
                className="w-1.5 h-1.5 bg-rose-400 rounded-full"
                animate={{ y: [0, -4, 0] }} transition={{ repeat: Infinity, duration: 0.6, ease: "easeInOut", delay: 0.15 }}
            />
            <motion.div
                className="w-1.5 h-1.5 bg-orange-400 rounded-full"
                animate={{ y: [0, -4, 0] }} transition={{ repeat: Infinity, duration: 0.6, ease: "easeInOut", delay: 0.3 }}
            />
        </div>
    </div>
);

export default function AICopilot({ user, portfolioContext }: AICopilotProps) {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState<Message[]>([
        { role: "model", text: "Welcome to Mars AI. How can I assist with your strategy today?", timestamp: Date.now() }
    ]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const [apiKey, setApiKey] = useState("");
    const chatContainerRef = useRef<HTMLDivElement>(null);

    // Load API key and chat history from localStorage
    useEffect(() => {
        const storedKey = localStorage.getItem("gemini_api_key");
        if (storedKey) setApiKey(storedKey);

        const storedHistory = localStorage.getItem(`marffet_chat_${user?.id || "guest"}`);
        if (storedHistory) {
            try {
                const parsed = JSON.parse(storedHistory);
                if (Array.isArray(parsed) && parsed.length > 0) {
                    setMessages(parsed);
                }
            } catch (e) {
                console.error("Failed to load chat history:", e);
            }
        }
    }, [user?.id]);

    // Save chat history on change
    useEffect(() => {
        if (messages.length > 1) {
            localStorage.setItem(`marffet_chat_${user?.id || "guest"}`, JSON.stringify(messages));
        }
    }, [messages, user?.id]);

    // Auto-scroll to bottom
    useEffect(() => {
        if (chatContainerRef.current) {
            chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
        }
    }, [messages, loading]);

    const isPremium = user?.is_admin || user?.is_premium;
    const isLoggedIn = !!user && user.id !== "guest";
    const hasServerKey = user?.has_gemini_key;
    const effectiveHasKey = apiKey || hasServerKey;

    const sendMessage = async () => {
        if (!input.trim() || loading) return;

        if (!effectiveHasKey) {
            setMessages([...messages, { role: "model", text: "Please configure your Gemini API Key directly in the settings below to chat.", timestamp: Date.now() }]);
            return;
        }

        const userMsg = input.trim();
        setMessages((prev) => [...prev, { role: "user", text: userMsg, timestamp: Date.now() }]);
        setInput("");
        setLoading(true);

        try {
            const res = await fetch(`${API_BASE}/api/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({
                    message: userMsg,
                    context: portfolioContext || "No portfolio data context currently available.",
                    apiKey: apiKey,
                    isPremium: isPremium
                })
            });

            const data = await res.json();
            if (res.ok) {
                setMessages((prev) => [...prev, { role: "model", text: data.response, timestamp: Date.now() }]);
            } else {
                setMessages((prev) => [...prev, { role: "model", text: `**System Notice:** ${data.error || "A connection error occurred."}`, timestamp: Date.now() }]);
            }
        } catch (e) {
            setMessages((prev) => [...prev, { role: "model", text: "Network timeout. Please check your connection and try again.", timestamp: Date.now() }]);
        } finally {
            setLoading(false);
        }
    };

    const saveApiKey = () => {
        if (apiKey.trim()) {
            localStorage.setItem("gemini_api_key", apiKey.trim());
        }
    };

    const clearChat = () => {
        const initialMsg: Message = { role: "model", text: "Chat cleared. What shall we analyze next?", timestamp: Date.now() };
        setMessages([initialMsg]);
        localStorage.removeItem(`marffet_chat_${user?.id || "guest"}`);
    };

    return (
        <>
            {/* Minimalist Floating Action Button */}
            <motion.button
                whileHover={isLoggedIn ? { scale: 1.05 } : {}}
                whileTap={isLoggedIn ? { scale: 0.95 } : {}}
                onClick={() => isLoggedIn && setIsOpen(!isOpen)}
                className={`fixed bottom-24 lg:bottom-6 right-6 w-14 h-14 rounded-full flex items-center justify-center shadow-2xl z-[50] transition-colors duration-300 ${isLoggedIn
                        ? "bg-gradient-to-br from-pink-600 to-amber-600 text-white shadow-pink-500/30 hover:shadow-pink-400/50 cursor-pointer"
                        : "bg-zinc-800 text-zinc-500 border border-white/5 cursor-not-allowed opacity-80"
                    }`}
                title={isLoggedIn ? "Access Copilot" : "Login Required"}
            >
                {isLoggedIn ? <SparklesIcon /> : <LockIcon />}
            </motion.button>

            {/* Main AI Chat Interface */}
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9, y: 30 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        transition={{ type: "spring", damping: 28, stiffness: 300 }}
                        className="fixed bottom-0 sm:bottom-24 right-0 sm:right-6 w-full sm:w-[420px] h-full sm:h-[600px] sm:max-h-[85vh] bg-[#0c0c0e]/95 backdrop-blur-2xl rounded-none sm:rounded-[2rem] flex flex-col z-[9999] overflow-hidden shadow-[0_8px_40px_rgba(0,0,0,0.4)] border-t sm:border border-white/10"
                    >
                        {/* Premium Header */}
                        <div className="relative bg-white/[0.02] p-5 shrink-0 border-b border-white/5 flex items-center justify-between">
                            {/* Ambient Glow */}
                            <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
                                <div className="absolute top-[-50%] left-[-20%] w-[140%] h-[150%] bg-gradient-to-r from-pink-500/10 via-purple-500/5 to-transparent rounded-full blur-2xl" />
                            </div>

                            <div className="relative z-10 flex items-center gap-3">
                                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-pink-500 to-rose-500 flex items-center justify-center shadow-[0_0_15px_rgba(236,72,153,0.3)]">
                                    <SparklesIcon />
                                </div>
                                <div>
                                    <h3 className="font-bold text-white tracking-tight flex items-center gap-2 text-sm">
                                        Mars Copilot
                                    </h3>
                                    <p className="text-[10px] text-zinc-400 font-medium">
                                        {isPremium ? (
                                            <span className="bg-gradient-to-r from-amber-400 to-orange-400 bg-clip-text text-transparent">Wealth Manager Mode</span>
                                        ) : (
                                            "Strategy Educator Mode"
                                        )}
                                    </p>
                                </div>
                            </div>

                            <div className="relative z-10 flex items-center gap-1">
                                <button
                                    onClick={clearChat}
                                    className="p-2 text-zinc-400 hover:text-white hover:bg-white/10 rounded-full transition-all"
                                    title="Reset Conversation"
                                >
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-4 h-4">
                                        <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
                                    </svg>
                                </button>
                                <button
                                    onClick={() => setIsOpen(false)}
                                    className="p-2 text-zinc-400 hover:text-white hover:bg-white/10 rounded-full transition-all"
                                >
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
                                        <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                </button>
                            </div>
                        </div>

                        {/* Scrollable Message List */}
                        <div
                            ref={chatContainerRef}
                            className="flex-1 overflow-y-auto p-5 space-y-5 scroll-smooth custom-scrollbar bg-black/20"
                        >
                            {messages.map((msg, idx) => (
                                <motion.div
                                    initial={{ opacity: 0, scale: 0.95, y: 10 }}
                                    animate={{ opacity: 1, scale: 1, y: 0 }}
                                    key={idx}
                                    className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                                >
                                    {msg.role === "model" && (
                                        <div className="w-6 h-6 rounded-full bg-gradient-to-br from-pink-500 to-rose-500 shrink-0 mr-2 mt-1 flex items-center justify-center">
                                            <SparklesIcon />
                                        </div>
                                    )}
                                    <div
                                        className={`max-w-[85%] px-4 py-3 text-[13.5px] leading-relaxed shadow-sm ${msg.role === "user"
                                                ? "bg-zinc-100 text-black font-medium rounded-2xl rounded-tr-sm"
                                                : "bg-[#1e1e24]/80 backdrop-blur-md text-zinc-200 border border-white/5 rounded-2xl rounded-tl-sm hover:border-white/10 transition-colors"
                                            }`}
                                    >
                                        <div className={`prose prose-sm max-w-none break-words [&>p]:mb-2 [&>p:last-child]:mb-0 [&>ul]:mb-2 [&>ul]:list-disc [&>ul]:ml-4 [&_code]:bg-black/30 [&_code]:rounded [&_code]:px-1.5 [&_code]:py-0.5 [&_code]:text-[12px] [&_pre]:bg-black/40 [&_pre]:p-3 [&_pre]:rounded-xl ${msg.role === "model" ? "prose-invert" : ""}`}>
                                            <ReactMarkdown>
                                                {msg.text}
                                            </ReactMarkdown>
                                        </div>
                                    </div>
                                </motion.div>
                            ))}
                            {loading && <ThinkingIndicator />}
                        </div>

                        {/* Config Missing Warning */}
                        <AnimatePresence>
                            {!effectiveHasKey && (
                                <motion.div
                                    initial={{ height: 0, opacity: 0 }}
                                    animate={{ height: "auto", opacity: 1 }}
                                    exit={{ height: 0, opacity: 0 }}
                                    className="px-5 py-4 bg-amber-500/10 border-t border-amber-500/20 backdrop-blur-xl shrink-0"
                                >
                                    <p className="text-[11px] text-amber-500 font-bold mb-2 uppercase tracking-wider flex items-center gap-1.5">
                                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-3.5 h-3.5">
                                            <path fillRule="evenodd" d="M18 10a8 8 0 1 1-16 0 8 8 0 0 1 16 0Zm-8-5a.75.75 0 0 1 .75.75v4.5a.75.75 0 0 1-1.5 0v-4.5A.75.75 0 0 1 10 5Zm0 10a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z" clipRule="evenodd" />
                                        </svg>
                                        API Key Required
                                    </p>
                                    <div className="flex gap-2 relative group">
                                        <div className="absolute -inset-0.5 bg-gradient-to-r from-amber-500 to-orange-500 rounded-xl blur opacity-20 group-hover:opacity-40 transition duration-500"></div>
                                        <input
                                            type="password"
                                            placeholder="sk-ant-..."
                                            value={apiKey}
                                            onChange={(e) => setApiKey(e.target.value)}
                                            className="relative flex-1 bg-black/60 border border-white/10 rounded-xl px-4 py-2.5 text-xs text-white placeholder-zinc-500 focus:border-amber-500/50 outline-none transition-all focus:bg-black/80"
                                        />
                                        <button
                                            onClick={saveApiKey}
                                            className="relative bg-gradient-to-r from-amber-500 to-orange-500 text-black px-4 py-2.5 rounded-xl text-xs font-bold hover:shadow-[0_0_15px_rgba(245,158,11,0.4)] transition-all active:scale-95"
                                        >
                                            Verify
                                        </button>
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        {/* Compact Input Area */}
                        <div className="p-4 bg-zinc-900/40 backdrop-blur-xl border-t border-white/5 shrink-0">
                            <div className="relative flex items-center bg-black/40 border border-white/10 rounded-2xl p-1 focus-within:border-pink-500/50 focus-within:bg-black/60 transition-all shadow-inner">
                                <input
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyDown={(e) => {
                                        if (e.key === "Enter" && !e.shiftKey) {
                                            e.preventDefault();
                                            if (!loading) sendMessage();
                                        }
                                    }}
                                    type="text"
                                    placeholder="Message Copilot..."
                                    className="flex-1 bg-transparent px-4 py-3 text-[13.5px] text-zinc-100 placeholder-zinc-500 outline-none w-full"
                                    disabled={loading}
                                />
                                <button
                                    onClick={sendMessage}
                                    disabled={loading || !input.trim()}
                                    className={`w-9 h-9 mr-1 rounded-xl flex items-center justify-center transition-all ${input.trim() && !loading
                                            ? "bg-white text-black shadow-[0_2px_10px_rgba(255,255,255,0.2)] hover:scale-105 active:scale-95"
                                            : "bg-white/5 text-zinc-500 cursor-not-allowed"
                                        }`}
                                >
                                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4 mr-0.5">
                                        <path d="M3.478 2.404a.75.75 0 0 0-.926.941l2.432 7.905H13.5a.75.75 0 0 1 0 1.5H4.984l-2.432 7.905a.75.75 0 0 0 .926.94 60.519 60.519 0 0 0 18.445-8.986.75.75 0 0 0 0-1.218A60.517 60.517 0 0 0 3.478 2.404Z" />
                                    </svg>
                                </button>
                            </div>
                            <div className="mt-2 text-center">
                                <p className="text-[9px] text-zinc-600 font-medium tracking-wide">
                                    AI insights may be inaccurate. Verify critical data independently.
                                </p>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Optional: Add basic scrollbar styling scoped just to this component tree 
                (Normally goes in global CSS, but acts as a quick polyfill here) */}
            <style jsx global>{`
                .custom-scrollbar::-webkit-scrollbar {
                    width: 6px;
                }
                .custom-scrollbar::-webkit-scrollbar-track {
                    background: transparent;
                }
                .custom-scrollbar::-webkit-scrollbar-thumb {
                    background: rgba(255,255,255,0.1);
                    border-radius: 10px;
                }
                .custom-scrollbar::-webkit-scrollbar-thumb:hover {
                    background: rgba(255,255,255,0.2);
                }
            `}</style>
        </>
    );
}
