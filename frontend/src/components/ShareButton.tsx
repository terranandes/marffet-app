"use client";

import { useState } from "react";

interface ShareButtonProps {
    title?: string;
    text?: string;
    url?: string;
    label?: string;
}

export default function ShareButton({
    title = "Martian Investment System",
    text = "Check out my investment stats!",
    url,
    label = "Share"
}: ShareButtonProps) {
    const [copied, setCopied] = useState(false);

    const handleShare = async () => {
        const shareUrl = url || window.location.href;

        // Try Native Share API first (Mobile)
        if (navigator.share) {
            try {
                await navigator.share({
                    title,
                    text,
                    url: shareUrl,
                });
                return;
            } catch (err) {
                console.warn("Share failed or canceled", err);
            }
        }

        // Fallback to Clipboard (Desktop)
        try {
            await navigator.clipboard.writeText(`${text}\n${shareUrl}`);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error("Clipboard copy failed", err);
        }
    };

    return (
        <button
            onClick={handleShare}
            className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium rounded-lg bg-white/10 hover:bg-white/20 transition text-[var(--color-text)]"
        >
            <span>{copied ? "✅ Copied!" : "📤"}</span>
            <span className={copied ? "text-green-400" : ""}>
                {copied ? "Link Copied" : label}
            </span>
        </button>
    );
}
