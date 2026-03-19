"use client";

import { Toaster } from "react-hot-toast";

export default function ToasterProvider() {
    return (
        <Toaster
            position="bottom-right"
            toastOptions={{
                duration: 3000,
                style: {
                    background: "rgba(14, 17, 23, 0.9)",
                    backdropFilter: "blur(8px)",
                    color: "#e0e0e0",
                    border: "1px solid rgba(255,255,255,0.05)",
                    fontSize: "14px",
                    borderRadius: "8px",
                    willChange: "transform",
                },
                success: {
                    style: {
                        borderLeft: "4px solid #10b981",
                        boxShadow: "0 4px 20px rgba(16, 185, 129, 0.2)",
                    },
                    iconTheme: {
                        primary: "#10b981",
                        secondary: "#1a1a2e",
                    },
                },
                error: {
                    style: {
                        borderLeft: "4px solid #ef4444",
                        boxShadow: "0 4px 20px rgba(239, 68, 68, 0.2)",
                    },
                    iconTheme: {
                        primary: "#ef4444",
                        secondary: "#1a1a2e",
                    },
                },
            }}
        />
    );
}
