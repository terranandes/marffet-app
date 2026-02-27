"use client";

import { Toaster } from "react-hot-toast";

export default function ToasterProvider() {
    return (
        <Toaster
            position="bottom-right"
            toastOptions={{
                duration: 3000,
                style: {
                    background: "#1a1a2e",
                    color: "#e0e0e0",
                    border: "1px solid rgba(255,255,255,0.1)",
                    fontSize: "14px",
                    borderRadius: "4px",
                },
                success: {
                    iconTheme: {
                        primary: "#10b981",
                        secondary: "#1a1a2e",
                    },
                },
                error: {
                    iconTheme: {
                        primary: "#ef4444",
                        secondary: "#1a1a2e",
                    },
                },
            }}
        />
    );
}
