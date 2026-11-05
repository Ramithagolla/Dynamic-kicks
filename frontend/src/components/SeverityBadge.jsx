import React from 'react';

export default function SeverityBadge({ severity, className = '' }) {
  const sev = (severity || 'Medium').toLowerCase();

  const styles = {
    critical: 'bg-red-950/80 text-red-400 border-red-800/80 shadow-[0_0_10px_rgba(239,68,68,0.2)]',
    high: 'bg-orange-950/80 text-orange-400 border-orange-800/80 shadow-[0_0_10px_rgba(249,115,22,0.2)]',
    medium: 'bg-amber-950/80 text-amber-400 border-amber-800/80',
    low: 'bg-emerald-950/80 text-emerald-400 border-emerald-800/80',
  };

  const style = styles[sev] || styles.medium;

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider border ${style} ${className}`}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current mr-1.5 animate-pulse" />
      {severity || 'Medium'}
    </span>
  );
}
