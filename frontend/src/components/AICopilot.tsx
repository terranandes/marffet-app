"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";

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

export default function AICopilot({ user, portfolioContext }: AICopilotProps) {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState<Message[]>([
        { role: "model", text: "Hello! I am Mars AI 🤖. How can I help you with your investments today?", timestamp: Date.now() }
    ]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const [apiKey, setApiKey] = useState("");
    const chatContainerRef = useRef<HTMLDivElement>(null);

    // Load API key and chat history from localStorage
    useEffect(() => {
        const storedKey = localStorage.getItem("gemini_api_key");
        if (storedKey) setApiKey(storedKey);

        const storedHistory = localStorage.getItem(`martian_chat_${user?.id || "guest"}`);
        if (storedHistory) {
            try {
                const parsed = JSON.parse(storedHistory);
                if (Array.isArray(parsed)) {
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
            localStorage.setItem(`martian_chat_${user?.id || "guest"}`, JSON.stringify(messages));
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
            setMessages([...messages, { role: "model", text: "Please set your Gemini API Key in the settings below to chat. 🔑", timestamp: Date.now() }]);
            return;
        }

        const userMsg = input;
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
                    context: portfolioContext || "No portfolio data available.",
                    apiKey: apiKey,
                    isPremium: isPremium
                })
            });

            const data = await res.json();
            if (res.ok) {
                setMessages((prev) => [...prev, { role: "model", text: data.response, timestamp: Date.now() }]);
            } else {
                setMessages((prev) => [...prev, { role: "model", text: `**Error:** ${data.error || "Unknown error"}`, timestamp: Date.now() }]);
            }
        } catch (e) {
            setMessages((prev) => [...prev, { role: "model", text: "Network Error. Please try again.", timestamp: Date.now() }]);
        } finally {
            setLoading(false);
        }
    };

    const saveApiKey = () => {
        localStorage.setItem("gemini_api_key", apiKey);
        setMessages((prev) => [...prev, { role: "model", text: "API Key saved! You can now chat with me. 🎉", timestamp: Date.now() }]);
    };

    const clearChat = () => {
        const initialMsg: Message = { role: "model", text: "Hello! I am Mars AI 🤖. How can I help you?", timestamp: Date.now() };
        setMessages([initialMsg]);
        localStorage.removeItem(`martian_chat_${user?.id || "guest"}`);
    };

    return (
        <>
            {/* FAB Button */}
            <button
                onClick={() => isLoggedIn && setIsOpen(!isOpen)}
                className={`fixed bottom-6 right-6 w-14 h-14 rounded-full flex items-center justify-center shadow-lg z-[9999] transition-all duration-300 ${isLoggedIn
                    ? "bg-gradient-to-tr from-pink-600 to-rose-400 hover:scale-110 shadow-[0_0_20px_rgba(255,0,85,0.4)]"
                    : "bg-zinc-700 opacity-50 cursor-not-allowed"
                    }`}
                title={isLoggedIn ? "Open AI Copilot" : "Login to use AI Copilot"}
            >
                <span className="text-2xl text-white">{isLoggedIn ? "🤖" : "🔒"}</span>
            </button>

            {/* Chat Panel */}
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        transition={{ type: "spring", damping: 25, stiffness: 300 }}
                        className="fixed bottom-0 sm:bottom-24 right-0 sm:right-6 w-full sm:w-[400px] h-full sm:h-[500px] bg-[#18181b]/95 backdrop-blur-md rounded-none sm:rounded-2xl flex flex-col z-[9999] overflow-hidden shadow-2xl border-t sm:border border-pink-500/30"
                    >
                        {/* Header */}
                        <div className="bg-gradient-to-r from-pink-500/20 to-rose-500/10 p-4 border-b border-white/5 flex justify-between items-center shrink-0">
                            <div className="flex items-center gap-2">
                                <h3 className="font-bold text-pink-400 flex items-center gap-2">🤖 Mars AI</h3>
                                {isPremium ? (
                                    <span className="text-[10px] bg-amber-500/20 text-amber-500 px-2 py-0.5 rounded-full border border-amber-500/30 font-bold uppercase tracking-wider">Premium</span>
                                ) : (
                                    <span className="text-[10px] bg-zinc-700 text-zinc-400 px-2 py-0.5 rounded-full font-bold uppercase tracking-wider">Free</span>
                                )}
                            </div>
                            <div className="flex items-center gap-3 text-zinc-400 text-sm">
                                <button onClick={clearChat} title="Clear Chat" className="p-1 hover:text-white transition">🗑️</button>
                                <button onClick={() => setIsOpen(false)} className="text-zinc-400 hover:text-white text-2xl leading-none transition">×</button>
                            </div>
                        </div>

                        {/* Messages */}
                        <div ref={chatContainerRef} className="flex-1 overflow-y-auto p-4 space-y-4 scroll-smooth">
                            {messages.map((msg, idx) => (
                                <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                                    <div
                                        className={`max-w-[85%] px-4 py-2.5 rounded-2xl text-sm leading-relaxed prose prose-sm prose-invert ${msg.role === "user"
                                            ? "bg-cyan-600 text-white font-medium rounded-tr-none shadow-lg shadow-cyan-900/20"
                                            : "bg-zinc-800 text-zinc-200 border border-white/5 rounded-tl-none"
                                            }`}
                                    >
                                        <ReactMarkdown
                                            components={{
                                                p: ({ node, ...props }) => <p className="mb-2 last:mb-0" {...props} />,
                                                ul: ({ node, ...props }) => <ul className="list-disc ml-4 mb-2" {...props} />,
                                                li: ({ node, ...props }) => <li className="mb-1" {...props} />,
                                                code: ({ node, ...props }) => <code className="bg-black/30 rounded px-1" {...props} />
                                            }}
                                        >
                                            {msg.text}
                                        </ReactMarkdown>
                                    </div>
                                </div>
                            ))}
                            {loading && (
                                <div className="flex justify-start">
                                    <div className="bg-zinc-800 p-3 rounded-2xl rounded-tl-none flex gap-1 items-center">
                                        <div className="w-1.5 h-1.5 bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                                        <div className="w-1.5 h-1.5 bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                                        <div className="w-1.5 h-1.5 bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* API Key Input (if not set AND no server key) */}
                        <AnimatePresence>
                            {!effectiveHasKey && (
                                <motion.div
                                    initial={{ height: 0, opacity: 0 }}
                                    animate={{ height: "auto", opacity: 1 }}
                                    className="px-4 py-3 bg-amber-950/20 border-t border-amber-500/20"
                                >
                                    <p className="text-[10px] text-amber-500 font-bold mb-2 uppercase tracking-wide">Action Required: API Key Missing</p>
                                    <div className="flex gap-2">
                                        <input
                                            type="password"
                                            placeholder="Gemini API Key..."
                                            value={apiKey}
                                            onChange={(e) => setApiKey(e.target.value)}
                                            className="flex-1 bg-black/40 border border-white/10 rounded-lg px-3 py-1.5 text-xs text-white focus:border-amber-500 outline-none"
                                        />
                                        <button
                                            onClick={saveApiKey}
                                            className="bg-amber-500 text-black px-3 py-1.5 rounded-lg text-xs font-bold hover:bg-amber-400 transition"
                                        >
                                            Save
                                        </button>
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        {/* Message Input */}
                        <div className="p-4 border-t border-white/5 bg-zinc-950/50 shrink-0">
                            <div className="flex gap-2 bg-zinc-900 border border-white/10 rounded-xl p-1 focus-within:border-pink-500/50 transition">
                                <input
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyDown={(e) => e.key === "Enter" && !loading && sendMessage()}
                                    type="text"
                                    placeholder="Message Mars AI..."
                                    className="flex-1 bg-transparent rounded-lg px-3 py-2 text-sm text-zinc-100 outline-none"
                                    disabled={loading}
                                />
                                <button
                                    onClick={sendMessage}
                                    disabled={loading || !input.trim()}
                                    className="bg-gradient-to-r from-pink-600 to-rose-500 text-white w-9 h-9 rounded-lg flex items-center justify-center font-bold hover:scale-105 active:scale-95 disabled:opacity-30 disabled:hover:scale-100 transition shadow-lg shadow-pink-900/20"
                                >
                                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                                        <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
                                    </svg>
                                </button>
                            </div>
                            <p className="text-[10px] text-zinc-600 mt-2 text-center text-balance">
                                Mars AI may provide inaccurate financial advice. Verify with TWSE/TPEx official data.
                            </p>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
}
