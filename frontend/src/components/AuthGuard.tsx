"use client";

import { usePathname } from "next/navigation";
import { useUser } from "@/lib/UserContext";
import { useLanguage } from "@/lib/i18n/LanguageContext";

export default function AuthGuard({ children }: { children: React.ReactNode }) {
    const { user, isLoading, login, refreshUser } = useUser();
    const pathname = usePathname();
    const { t } = useLanguage();

    // Only allow Home page (/) to be accessed without a session.
    // All other tabs require a login (user or guest).
    const isPublicPage = pathname === "/" || pathname === "/auth/login";

    if (isLoading) {
        return (
            <div className="flex h-[50vh] items-center justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[var(--color-cta)]"></div>
            </div>
        );
    }

    if (!user && !isPublicPage) {
        return (
            <div className="flex flex-col items-center justify-center h-[70vh] px-4">
                <div className="w-24 h-24 mb-6 rounded-full bg-zinc-800 flex items-center justify-center border-4 border-zinc-700 shadow-inner">
                    <span className="text-zinc-500 text-4xl">🔒</span>
                </div>
                <h2 className="text-2xl md:text-3xl font-bold text-white mb-3 text-center">
                    Authentication Required
                </h2>
                <p className="text-zinc-400 text-center max-w-md mb-8">
                    To access {pathname.substring(1).charAt(0).toUpperCase() + pathname.substring(2)} and prevent unnecessary background processing, please sign in with Google or continue as a Guest.
                </p>

                <div className="flex flex-col sm:flex-row gap-4 w-full max-w-sm">
                    <button
                        onClick={() => login()}
                        className="flex-1 flex items-center justify-center gap-2 py-3 bg-white text-black font-bold rounded-xl hover:bg-zinc-200 transition-all shadow-lg hover:shadow-xl"
                    >
                        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12.545,10.239v3.821h5.445c-0.712,2.315-2.647,3.972-5.445,3.972c-3.332,0-6.033-2.701-6.033-6.032s2.701-6.032,6.033-6.032c1.498,0,2.866,0.549,3.921,1.453l2.814-2.814C17.503,2.988,15.139,2,12.545,2C7.021,2,2.543,6.477,2.543,12s4.478,10,10.002,10c8.396,0,10.249-7.85,9.426-11.748L12.545,10.239z" />
                        </svg>
                        {t('Sidebar.SignInGoogle') || "Sign in with Google"}
                    </button>
                    <button
                        onClick={() => {
                            try {
                                console.log("Activating Guest Mode from AuthGuard");
                                localStorage.setItem("marffet_guest_mode", "true");
                                refreshUser();
                            } catch (e) {
                                console.error("Guest mode error:", e);
                                alert("Failed to activate guest mode locally");
                            }
                        }}
                        className="flex-1 flex items-center justify-center gap-2 py-3 bg-white/10 text-white font-bold rounded-xl hover:bg-white/20 transition-all border border-white/10"
                    >
                        {t('Sidebar.ExploreGuest') || "Explore as Guest"}
                    </button>
                </div>
            </div>
        );
    }

    return <>{children}</>;
}
