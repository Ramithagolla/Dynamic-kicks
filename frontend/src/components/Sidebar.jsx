import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  SearchCode,
  ShieldAlert,
  Brain,
  BarChart3,
  Shield,
  Cpu
} from 'lucide-react';

const navItems = [
  { name: 'Overview', path: '/', icon: LayoutDashboard },
  { name: 'Investigate Threat', path: '/investigate', icon: SearchCode },
  { name: 'Incidents', path: '/incidents', icon: ShieldAlert },
  { name: 'Memory Explorer', path: '/memory', icon: Brain },
  { name: 'Learning Analytics', path: '/analytics', icon: BarChart3 },
];

export default function Sidebar({ memoryStatus }) {
  return (
    <aside className="w-64 bg-[#0d1322] border-r border-slate-800 flex flex-col shrink-0 h-screen sticky top-0">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white shadow-[0_0_15px_rgba(59,130,246,0.3)]">
            <Shield className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-slate-100 text-lg tracking-tight flex items-center gap-1.5">
              ThreatLens <span className="text-xs px-1.5 py-0.5 rounded bg-blue-600/30 text-blue-400 font-mono border border-blue-500/30">AI</span>
            </h1>
            <p className="text-[10px] text-slate-400 font-medium tracking-wide uppercase">
              Multi-Agent SOC Platform
            </p>
          </div>
        </div>
        <div className="mt-3 text-[11px] text-slate-400 italic">
          Detect. Investigate. Remember. Defend.
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        <div className="px-3 py-2 text-[10px] font-semibold tracking-wider text-slate-400 uppercase">
          SOC Operations
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-blue-600/15 text-blue-400 border border-blue-500/30 shadow-[0_0_12px_rgba(59,130,246,0.15)]'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`
              }
            >
              <Icon className="w-4 h-4" />
              <span>{item.name}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Memory Bank Status Footer */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-900/40">
        <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80">
          <div className="flex items-center justify-between text-xs mb-1.5">
            <span className="flex items-center gap-1.5 text-slate-400 font-medium">
              <Brain className="w-3.5 h-3.5 text-purple-400" />
              Hindsight Bank
            </span>
            <span
              className={`w-2 h-2 rounded-full ${
                memoryStatus?.status === 'connected'
                  ? 'bg-emerald-400 shadow-[0_0_8px_#34d399]'
                  : 'bg-amber-400'
              }`}
            />
          </div>
          <div className="text-[11px] font-mono text-slate-300 truncate font-semibold">
            threatlens-security-memory
          </div>
          <div className="mt-1 flex items-center justify-between text-[10px] text-slate-400">
            <span>Status:</span>
            <span className="capitalize text-slate-300 font-medium">
              {memoryStatus?.status || 'Operational'}
            </span>
          </div>
        </div>

        <div className="mt-3 flex items-center justify-between text-[10px] text-slate-400 px-1">
          <span className="flex items-center gap-1">
            <Cpu className="w-3 h-3 text-blue-400" /> 5 Active Agents
          </span>
          <span className="font-mono">v1.0</span>
        </div>
      </div>
    </aside>
  );
}
