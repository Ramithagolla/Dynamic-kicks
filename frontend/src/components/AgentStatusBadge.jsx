import React from 'react';
import { ShieldCheck, Cpu, Database, Award, Crosshair } from 'lucide-react';

export default function AgentStatusBadge({ agentName, status = 'available', customLabel, role, executionCount }) {
  const agentIcons = {
    'detection': ShieldCheck,
    'investigation': Crosshair,
    'memory': Database,
    'response': Cpu,
    'learning': Award,
  };

  const IconComponent = agentIcons[agentName?.toLowerCase()] || ShieldCheck;
  const normalizedStatus = (status || 'available').toLowerCase();

  const getStatusConfig = () => {
    switch (normalizedStatus) {
      case 'active':
      case 'available':
      case 'completed':
        return {
          dotClass: 'bg-emerald-400 animate-pulse',
          textClass: 'text-emerald-400',
          badgeText: normalizedStatus === 'available' ? 'Available' : normalizedStatus === 'completed' ? 'Completed' : 'Active',
          borderClass: 'border-slate-800'
        };
      case 'running':
        return {
          dotClass: 'bg-blue-400 animate-ping',
          textClass: 'text-blue-400',
          badgeText: 'Running',
          borderClass: 'border-blue-500/30 bg-blue-950/20'
        };
      case 'degraded':
        return {
          dotClass: 'bg-amber-400',
          textClass: 'text-amber-400',
          badgeText: 'Degraded',
          borderClass: 'border-amber-900/30'
        };
      case 'registered':
        return {
          dotClass: 'bg-slate-500',
          textClass: 'text-slate-400',
          badgeText: 'Registered',
          borderClass: 'border-slate-800'
        };
      case 'failed':
      case 'unavailable':
      case 'offline':
        return {
          dotClass: 'bg-red-400',
          textClass: 'text-red-400',
          badgeText: normalizedStatus === 'unavailable' ? 'Unavailable' : 'Failed',
          borderClass: 'border-red-900/30 bg-red-950/10'
        };
      default:
        return {
          dotClass: 'bg-slate-400',
          textClass: 'text-slate-400',
          badgeText: normalizedStatus,
          borderClass: 'border-slate-800'
        };
    }
  };

  const cfg = getStatusConfig();

  return (
    <div className={`flex items-start gap-2.5 px-3 py-2 rounded-lg bg-slate-900/80 border ${cfg.borderClass} text-xs transition`}>
      <div className="p-1.5 rounded bg-blue-950/60 text-blue-400 border border-blue-900/40 shrink-0 mt-0.5">
        <IconComponent className="w-3.5 h-3.5" />
      </div>
      <div className="min-w-0 flex-1">
        <div className="text-slate-200 font-semibold leading-tight truncate">
          {customLabel || agentName}
        </div>
        {role && (
          <div className="text-[10px] text-slate-500 truncate leading-tight mt-0.5">
            {role}
          </div>
        )}
        <div className="flex items-center justify-between gap-1 text-[10px] mt-1">
          <div className="flex items-center gap-1.5">
            <span className={`w-1.5 h-1.5 rounded-full ${cfg.dotClass}`} />
            <span className={`font-mono font-medium ${cfg.textClass}`}>{cfg.badgeText}</span>
          </div>
          {typeof executionCount === 'number' && (
            <span className="text-slate-500 font-mono text-[9px]">
              {executionCount} runs
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
