import React, { useState } from 'react';
import { Rocket, BarChart3, LineChart, Settings, Sliders } from 'lucide-react';
import { cn } from './lib/utils';
import MarsStrategy from './components/MarsStrategy';
import CBStrategy from './components/CBStrategy';
import Visualization from './components/Visualization';

function App() {
  const [activeTab, setActiveTab] = useState<'mars' | 'cb' | 'viz'>('mars');

  return (
    <div className="flex h-screen bg-slate-50 text-slate-900 font-sans">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 text-slate-50 flex flex-col border-r border-slate-800">
        <div className="p-6 border-b border-slate-800 flex items-center gap-3">
          <div className="p-2 bg-blue-600 rounded-lg">
            <Rocket className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight">Martian</h1>
            <p className="text-xs text-slate-400">Investment System</p>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          <SidebarItem
            active={activeTab === 'mars'}
            onClick={() => setActiveTab('mars')}
            icon={<LineChart className="w-5 h-5" />}
            label="Mars Strategy"
          />
          <SidebarItem
            active={activeTab === 'cb'}
            onClick={() => setActiveTab('cb')}
            icon={<Sliders className="w-5 h-5" />}
            label="CB Arbitrage"
          />
          <SidebarItem
            active={activeTab === 'viz'}
            onClick={() => setActiveTab('viz')}
            icon={<BarChart3 className="w-5 h-5" />}
            label="Visualization"
          />
        </nav>

        <div className="p-4 border-t border-slate-800">
          <button className="flex items-center gap-3 px-4 py-3 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg w-full transition-colors">
            <Settings className="w-5 h-5" />
            <span className="font-medium">Settings</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto bg-slate-50 relative">
        <div className="max-w-7xl mx-auto p-8">
          {activeTab === 'mars' && <MarsStrategy />}
          {activeTab === 'cb' && <CBStrategy />}
          {activeTab === 'viz' && <Visualization />}
        </div>
      </main>
    </div>
  );
}

function SidebarItem({ active, onClick, icon, label }: { active: boolean, onClick: () => void, icon: React.ReactNode, label: string }) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "flex items-center gap-3 px-4 py-3 rounded-lg w-full transition-all duration-200 group",
        active
          ? "bg-blue-600 text-white shadow-lg shadow-blue-900/20"
          : "text-slate-400 hover:text-white hover:bg-slate-800"
      )}
    >
      {icon}
      <span className="font-medium">{label}</span>
      {active && <div className="ml-auto w-1.5 h-1.5 rounded-full bg-white animate-pulse" />}
    </button>
  );
}

export default App;
