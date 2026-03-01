"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import en from "./locales/en.json";
import zhTW from "./locales/zh-TW.json";
import zhCN from "./locales/zh-CN.json";

export type Language = "en" | "zh-TW" | "zh-CN";

// Map JSONs to explicit any to allow dynamic nested access
const translations: Record<Language, any> = {
    "en": en,
    "zh-TW": zhTW,
    "zh-CN": zhCN
};

interface LanguageContextType {
    language: Language;
    setLanguage: (lang: Language) => void;
    t: (key: string, params?: Record<string, string | number>) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: ReactNode }) {
    const [language, setLanguageState] = useState<Language>("en");
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        const savedLang = localStorage.getItem("martian_lang") as Language;
        if (savedLang && ["en", "zh-TW", "zh-CN"].includes(savedLang)) {
            setLanguageState(savedLang);
        }
        setMounted(true);
    }, []);

    const setLanguage = (lang: Language) => {
        setLanguageState(lang);
        localStorage.setItem("martian_lang", lang);
    };

    const t = (key: string, params?: Record<string, string | number>) => {
        // Simple nested key access e.g., "Settings.Profile"
        const keys = key.split(".");
        let text: any = translations[language];

        for (const k of keys) {
            if (text && typeof text === "object") {
                text = text[k];
            } else {
                text = undefined;
                break;
            }
        }

        // Fallback to English
        if (text === undefined && language !== "en") {
            let fallbackText: any = translations["en"];
            for (const k of keys) {
                if (fallbackText && typeof fallbackText === "object") {
                    fallbackText = fallbackText[k];
                } else {
                    fallbackText = undefined;
                    break;
                }
            }
            text = fallbackText;
        }

        // Final fallback if missing entirely
        if (text === undefined) return key;

        // Interpolation
        if (params && typeof text === "string") {
            return Object.entries(params).reduce(
                (acc, [k, v]) => acc.replace(new RegExp(`{${k}}`, 'g'), String(v)),
                text
            );
        }

        return typeof text === "string" ? text : key;
    };

    // Note: Hydration mismatch on client side initial load might occur for non-English users,
    // which is standard for client-side localStorage preferences. 
    // We render children regardless.
    return (
        <LanguageContext.Provider value={{ language, setLanguage, t }}>
            {children}
        </LanguageContext.Provider>
    );
}

export function useLanguage() {
    const context = useContext(LanguageContext);
    if (context === undefined) {
        throw new Error("useLanguage must be used within a LanguageProvider");
    }
    return context;
}
