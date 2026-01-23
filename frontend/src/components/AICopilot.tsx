"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface Message {
    role: "user" | "model";
    text: string;
}

interface AICopilotProps {
    user: any;
    portfolioContext?: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function AICopilot({ user, portfolioContext }: AICopilotProps) {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState<Message[]>([
        { role: "model", text: "Hello! I am Mars AI 🤖. How can I help you with your investments today?" }
    ]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const [apiKey, setApiKey] = useState("");
    const chatContainerRef = useRef<HTMLDivElement>(null);

    // Load API key from localStorage
    useEffect(() => {
        const stored = localStorage.getItem("gemini_api_key");
        if (stored) setApiKey(stored);
    }, []);

    // Auto-scroll to bottom
    useEffect(() => {
        if (chatContainerRef.current) {
            chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
        }
    }, [messages]);

    const isPremium = user?.is_admin || (user?.subscription_tier && user.subscription_tier > 0);
    const isLoggedIn = !!user && user.id !== "guest";

    const sendMessage = async () => {
        if (!input.trim()) return;

        if (!apiKey) {
            setMessages([...messages, { role: "model", text: "Please set your Gemini API Key in the input below to chat. 🔑" }]);
            return;
        }

        const userMsg = input;
        setMessages((prev) => [...prev, { role: "user", text: userMsg }]);
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
                setMessages((prev) => [...prev, { role: "model", text: data.response }]);
            } else {
                setMessages((prev) => [...prev, { role: "model", text: `Error: ${data.error || "Unknown error"}` }]);
            }
        } catch (e) {
            setMessages((prev) => [...prev, { role: "model", text: "Network Error. Please try again." }]);
        } finally {
            setLoading(false);
        }
    };

    const saveApiKey = () => {
        localStorage.setItem("gemini_api_key", apiKey);
        setMessages((prev) => [...prev, { role: "model", text: "API Key saved! You can now chat with me. 🎉" }]);
    };

    return (
        <>
            {/* FAB Button */}
            <button
                onClick={() => isLoggedIn && setIsOpen(!isOpen)}
                className={`fixed bottom-6 right-6 w-14 h-14 rounded-full flex items-center justify-center shadow-lg z-[9999] transition-all duration-200 ${isLoggedIn
                        ? "bg-pink-500 hover:bg-pink-600 hover:scale-110 shadow-[0_0_20px_rgba(255,0,85,0.4)]"
                        : "bg-gray-600 opacity-50 cursor-not-allowed"
                    }`}
                title={isLoggedIn ? "Open AI Copilot" : "Login to use AI Copilot"}
            >
                <span className="text-2xl text-white">{isLoggedIn ? "🤖" : "🔒"}</span>
            </button>

            {/* Chat Panel */}
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: 50, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 50, scale: 0.95 }}
                        transition={{ duration: 0.2 }}
                        className="fixed bottom-24 right-6 w-80 h-[420px] bg-zinc-900/95 backdrop-blur-sm rounded-xl flex flex-col z-[9999] overflow-hidden shadow-2xl border border-pink-500/30"
                    >
                        {/* Header */}
                        <div className="bg-pink-500/10 p-3 border-b border-pink-500/20 flex justify-between items-center">
                            <h3 className="font-bold text-pink-400 flex items-center gap-2">🤖 Mars AI Copilot</h3>
                            <button onClick={() => setIsOpen(false)} className="text-gray-400 hover:text-white text-xl">
                                ×
                            </button>
                        </div>

                        {/* Messages */}
                        <div ref={chatContainerRef} className="flex-1 overflow-y-auto p-4 space-y-3">
                            {messages.map((msg, idx) => (
                                <div key={idx} className={msg.role === "user" ? "text-right" : "text-left"}>
                                    <div
                                        className={`inline-block max-w-[85%] px-3 py-2 rounded-lg text-sm ${msg.role === "user"
                                                ? "bg-cyan-500 text-black font-medium"
                                                : "bg-zinc-700 text-gray-200"
                                            }`}
                                    >
                                        {msg.text}
                                    </div>
                                </div>
                            ))}
                            {loading && (
                                <div className="text-xs text-gray-500 animate-pulse italic">Thinking...</div>
                            )}
                        </div>

                        {/* API Key Input (if not set) */}
                        {!apiKey && (
                            <div className="p-2 bg-yellow-900/30 border-t border-yellow-500/30">
                                <div className="flex gap-2">
                                    <input
                                        type="password"
                                        placeholder="Enter Gemini API Key..."
                                        value={apiKey}
                                        onChange={(e) => setApiKey(e.target.value)}
                                        className="flex-1 bg-black/50 border border-yellow-500/30 rounded px-2 py-1 text-xs text-white focus:border-yellow-500 outline-none"
                                    />
                                    <button
                                        onClick={saveApiKey}
                                        className="bg-yellow-500 text-black px-2 py-1 rounded text-xs font-bold hover:bg-yellow-400"
                                    >
                                        Save
                                    </button>
                                </div>
                            </div>
                        )}

                        {/* Message Input */}
                        <div className="p-3 border-t border-white/10 bg-black/20">
                            <div className="flex gap-2">
                                <input
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                                    type="text"
                                    placeholder="Ask Mars AI..."
                                    className="flex-1 bg-black/50 border border-white/20 rounded px-3 py-2 text-sm text-white focus:border-pink-500 outline-none"
                                />
                                <button
                                    onClick={sendMessage}
                                    disabled={loading}
                                    className="bg-pink-500 text-white px-3 py-2 rounded text-sm font-bold hover:bg-pink-600 disabled:opacity-50"
                                >
                                    ➤
                                </button>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
}
