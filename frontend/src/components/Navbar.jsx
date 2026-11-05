import React, { useState, useEffect } from 'react';
import { Shield, Brain, Sparkles, Activity, AlertTriangle, Plus } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Navbar({ healthData }) {
  const [currentTime, setCurrentTime] = useState(new Date().toUTCString());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date().toUTCString());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const hindsightStatus = healthData?.hindsight?.status || 'active';
  const mongoMode = healthData?.mongodb?.mode || 'database';

  return (
    <header className="h-16 bg-[#0d1322]/90 backdrop-blur border-b border-slate-800 px-6 flex items-center justify-between sticky top-0 z-30">
      {/* Left: SOC Time & Breadcrumbs */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 text-xs text-slate-400 font-mono bg-slate-900/80 px-3 py-1.5 rounded-md border border-slate-800">
          <Activity className="w-3.5 h-3.5 text-blue-400 animate-pulse" />
          <span>SOC UTC: {currentTime}</span>
        </div>

        <div className="hidden md:flex items-center gap-1.5 text-xs text-slate-400">
          <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
          <span>Storage:</span>
          <span className="text-slate-300 font-mono text-[11px] bg-slate-800/60 px-1.5 py-0.5 rounded">
            {mongoMode.includes('mock') ? 'MongoDB (Local In-Memory)' : 'MongoDB Cluster'}
          </span>
        </div>
      </div>

      {/* Right: Health Badges & New Investigation */}
      <div className="flex items-center gap-3">
        {/* Hindsight Status Pill */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-purple-950/40 border border-purple-800/50 text-xs">
          <Brain className="w-3.5 h-3.5 text-purple-400" />
          <span className="text-slate-300">Hindsight:</span>
          <span className="capitalize font-medium text-purple-300">
            {hindsightStatus}
          </span>
        </div>

        {/* Quick Action Button */}
        <Link
          to="/investigate"
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-[0_0_12px_rgba(59,130,246,0.3)] transition"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>New Investigation</span>
        </Link>
      </div>
    </header>
  );
}
