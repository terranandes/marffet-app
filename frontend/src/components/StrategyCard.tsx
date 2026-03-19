import Link from "next/link";
import { useLanguage } from "@/lib/i18n/LanguageContext";

interface Metric {
    label: string;
    value: string;
}

interface StrategyCardProps {
    title: string;
    description: string;
    href: string;
    icon: string;
    status: "active" | "dev" | "inactive";
    metrics?: Metric[];
}

export default function StrategyCard({
    title,
    description,
    href,
    icon,
    status,
    metrics,
}: StrategyCardProps) {
    const { t } = useLanguage();

    return (
        <Link
            href={href}
            className="group relative flex flex-col justify-between overflow-hidden rounded-2xl bg-zinc-900/50 border border-zinc-800 p-6 hover:border-zinc-700 transition-all duration-300 hover:shadow-2xl hover:-translate-y-1"
        >
            {/* Background Gradient Effect */}
            <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

            <div>
                <div className="flex justify-between items-start mb-4">
                    <div className="text-4xl">{icon}</div>
                    {status === "active" ? (
                        <span className="px-2 py-1 rounded text-[10px] uppercase font-bold bg-green-500/10 text-green-400 border border-green-500/20">
                            {t('Home.ActiveBadge')}
                        </span>
                    ) : (
                        <span className="px-2 py-1 rounded text-[10px] uppercase font-bold bg-yellow-500/10 text-yellow-400 border border-yellow-500/20">
                            {t('Home.DevBadge')}
                        </span>
                    )}
                </div>

                <h3 className="text-xl font-bold text-white mb-2 group-hover:text-[var(--color-cta)] transition-colors">
                    {title}
                </h3>
                <p className="text-zinc-400 text-sm leading-relaxed mb-6">
                    {description}
                </p>
            </div>

            {metrics && metrics.length > 0 && (
                <div className="grid grid-cols-2 gap-2 pt-4 border-t border-white/5">
                    {metrics.map((m, i) => (
                        <div key={i}>
                            <div className="text-xs text-zinc-500">{m.label}</div>
                            <div className="text-sm font-bold text-white font-mono">{m.value}</div>
                        </div>
                    ))}
                </div>
            )}
        </Link>
    );
}
