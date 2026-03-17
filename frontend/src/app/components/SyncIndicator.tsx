import { RefreshCw } from "lucide-react";

export function SyncIndicator({ isSyncing }: { isSyncing: boolean }) {
  if (!isSyncing) return null;
  return (
    <div className="fixed bottom-4 right-4 bg-terran-blue/20 backdrop-blur-md border border-terran-blue/30 text-terran-blue px-3 py-1.5 rounded-full text-xs font-medium flex items-center gap-2 z-50 animate-in fade-in slide-in-from-bottom-4 shadow-[0_0_15px_rgba(0,195,255,0.2)]">
      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
      <span>Syncing...</span>
    </div>
  );
}
