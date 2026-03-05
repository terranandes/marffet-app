"use client";

import { motion } from "framer-motion";

export default function PageTransition({ children }: { children: React.ReactNode }) {
    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.98, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{
                duration: 0.3,
                ease: [0.22, 1, 0.36, 1] // Apple-like spring/ease
            }}
            className="w-full"
        >
            {children}
        </motion.div>
    );
}
