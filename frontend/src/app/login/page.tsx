"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useUser } from "@/lib/UserContext";
import { useLanguage } from "@/lib/i18n/LanguageContext";

export default function LoginPage() {
    const { user, isLoading, login, refreshUser } = useUser();
    const { t } = useLanguage();
    const router = useRouter();
    const [isGuestLoading, setIsGuestLoading] = useState(false);

    // Redirect to home if already logged in
    useEffect(() => {
        if (!isLoading && user) {
            router.replace("/");
        }
    }, [isLoading, user, router]);

    const handleGuestLogin = async () => {
        setIsGuestLoading(true);
        try {
            const res = await fetch("/auth/guest", {
                method: "POST",
                credentials: "include"
            });
            if (res.ok) {
                await refreshUser();
                router.replace("/");
            } else {
                console.error("Guest login failed");
            }
        } catch (e) {
            console.error("Guest login error:", e);
        } finally {
            setIsGuestLoading(false);
        }
    };

    if (isLoading || user) {
        return (
            <div className="flex items-center justify-center min-h-[60vh]">
                <div className="w-12 h-12 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
        );
    }

    return (
        <div className="flex flex-col items-center justify-center min-h-[70vh] w-full max-w-md mx-auto px-4 py-12 animate-fade-in">
            {/* Logo Area */}
            <div className="mb-10 flex flex-col items-center">
                <div className="w-20 h-20 rounded-2xl bg-gradient-to-tr from-[var(--color-cta)] to-blue-500 shadow-[0_0_30px_rgba(139,92,246,0.5)] flex items-center justify-center text-white font-extrabold text-4xl mb-6">
                    M
                </div>
                <h1 className="text-3xl font-extrabold bg-gradient-to-r from-white to-[var(--color-cta)] bg-clip-text text-transparent">
                    MARFFET
                </h1>
                <p className="text-zinc-400 mt-2 text-center max-w-sm">
                    {t('Home.Title') || "Advanced Low-Volatility Stock Analysis & Portfolio Tracking"}
                </p>
            </div>

            {/* Login Card */}
            <div className="w-full bg-[#0e1117]/80 backdrop-blur-xl border border-zinc-800 rounded-3xl p-8 shadow-2xl relative overflow-hidden">
                <div className="absolute top-0 inset-x-0 h-px bg-gradient-to-r from-transparent via-cyan-500/50 to-transparent"></div>

                <h2 className="text-xl font-bold text-white mb-8 text-center">
                    {t('Sidebar.SignInGoogle') ? t('Sidebar.SignInGoogle').replace('with Google', '') : "Sign In"}
                </h2>

                <div className="space-y-4">
                    {/* Google Login */}
                    <button
                        onClick={login}
                        className="flex items-center justify-center gap-3 w-full py-4 bg-white text-black font-bold rounded-2xl hover:bg-zinc-200 transition-all shadow-[0_0_15px_rgba(255,255,255,0.1)] hover:shadow-[0_0_20px_rgba(255,255,255,0.3)] hover:-translate-y-0.5"
                    >
                        <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12.545,10.239v3.821h5.445c-0.712,2.315-2.647,3.972-5.445,3.972c-3.332,0-6.033-2.701-6.033-6.032s2.701-6.032,6.033-6.032c1.498,0,2.866,0.549,3.921,1.453l2.814-2.814C17.503,2.988,15.139,2,12.545,2C7.021,2,2.543,6.477,2.543,12s4.478,10,10.002,10c8.396,0,10.249-7.85,9.426-11.748L12.545,10.239z" />
                        </svg>
                        {t('Sidebar.SignInGoogle') || "Sign in with Google"}
                    </button>

                    <div className="flex items-center gap-4 my-6">
                        <div className="h-px bg-zinc-800 flex-1"></div>
                        <span className="text-xs text-zinc-500 font-medium uppercase tracking-widest">OR</span>
                        <div className="h-px bg-zinc-800 flex-1"></div>
                    </div>

                    {/* Guest Login */}
                    <button
                        onClick={handleGuestLogin}
                        disabled={isGuestLoading}
                        className="flex items-center justify-center gap-3 w-full py-4 bg-transparent text-white border-2 border-zinc-800 font-bold rounded-2xl hover:border-zinc-700 hover:bg-zinc-800/50 transition-all group disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isGuestLoading ? (
                            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        ) : (
                            <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6 text-zinc-400 group-hover:text-white transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                            </svg>
                        )}
                        {t('Sidebar.ExploreGuest') || "Explore as Guest"}
                    </button>

                    <p className="text-xs text-zinc-500 text-center mt-4">
                        Guest data is stored locally on your device only.
                    </p>
                </div>
            </div>

            <div className="mt-12 text-center text-xs text-zinc-600">
                v0.2.1 • Secure Authentication
            </div>
        </div>
    );
}
