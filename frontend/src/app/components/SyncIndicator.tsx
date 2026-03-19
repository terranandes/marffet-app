export function SyncIndicator({ isSyncing }: { isSyncing: boolean }) {
  if (!isSyncing) return null;
  return (
    <div className="fixed bottom-4 right-4 bg-terran-blue/20 backdrop-blur-md border border-terran-blue/30 text-terran-blue px-3 py-1.5 rounded-full text-xs font-medium flex items-center gap-2 z-50 animate-in fade-in slide-in-from-bottom-4 shadow-[0_0_15px_rgba(0,195,255,0.2)]">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-3.5 h-3.5 animate-spin"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/><path d="M16 21v-5h5"/></svg>
      <span>Syncing...</span>
    </div>
  );
}
