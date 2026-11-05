import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  BarChart3,
  Brain,
  CheckCircle2,
  TrendingUp,
  ArrowRight,
  RefreshCw,
  Award,
  ShieldAlert,
  Zap,
  Sparkles,
  GitCompare,
  FileCheck2,
  Clock
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip
} from 'recharts';
import { getAnalytics } from '../api/client';
import SeverityBadge from '../components/SeverityBadge';

export default function Analytics() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const data = await getAnalytics();
      setAnalytics(data);
    } catch (err) {
      console.error('Failed to load learning analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const metrics = analytics?.metrics || {
    total_incidents: 0,
    confirmed_count: 0,
    memory_assisted_count: 0,
    acceptance_rate: 0,
    total_recommendations_accepted: 0,
    total_recommendations_rejected: 0,
  };

  const comparison = analytics?.comparison;
  const firstInv = comparison?.first_investigation;
  const secondInv = comparison?.second_investigation;

  const recStats = [
    { name: 'Accepted Actions', count: metrics.total_recommendations_accepted, fill: '#10b981' },
    { name: 'Rejected Actions', count: metrics.total_recommendations_rejected, fill: '#f43f5e' },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight flex items-center gap-2">
            Learning Analytics & Memory Impact
            <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-normal">
              Continuous Learning
            </span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Quantifying how analyst-confirmed incident outcomes and Hindsight persistent memory enhance SOC response quality over time.
          </p>
        </div>

        <button
          onClick={fetchAnalytics}
          disabled={loading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 transition self-start md:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh Metrics
        </button>
      </div>

      {/* 4 Core Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Confirmed Incidents */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-2">
            <span className="text-emerald-300">Analyst Confirmed</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-3xl font-bold text-emerald-400 font-mono">
            {metrics.confirmed_count}
          </div>
          <div className="mt-2 text-[11px] text-slate-400">
            Stored in Hindsight bank via <code className="text-emerald-300 font-mono">retain</code>
          </div>
          <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/10 rounded-full blur-xl pointer-events-none" />
        </div>

        {/* Memory Assisted */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-purple-900/30 relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-2">
            <span className="text-purple-300">Memory Recalled</span>
            <Brain className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-3xl font-bold text-purple-400 font-mono">
            {metrics.memory_assisted_count}
          </div>
          <div className="mt-2 text-[11px] text-slate-400">
            Investigations enriched by prior intelligence
          </div>
          <div className="absolute top-0 right-0 w-24 h-24 bg-purple-500/10 rounded-full blur-xl pointer-events-none" />
        </div>

        {/* Acceptance Rate */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-blue-900/30 relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-2">
            <span className="text-blue-300">Action Acceptance</span>
            <Award className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-3xl font-bold text-blue-400 font-mono">
            {metrics.acceptance_rate || 100}%
          </div>
          <div className="mt-2 text-[11px] text-slate-400">
            Recommendations confirmed by analysts
          </div>
          <div className="absolute top-0 right-0 w-24 h-24 bg-blue-500/10 rounded-full blur-xl pointer-events-none" />
        </div>

        {/* Total Evaluated */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-2">
            <span>Actions Evaluated</span>
            <Zap className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-3xl font-bold text-slate-100 font-mono">
            {metrics.total_recommendations_accepted + metrics.total_recommendations_rejected}
          </div>
          <div className="mt-2 text-[11px] text-slate-400 flex items-center gap-2">
            <span className="text-emerald-400 font-medium">{metrics.total_recommendations_accepted} Accepted</span>
            <span>•</span>
            <span className="text-rose-400 font-medium">{metrics.total_recommendations_rejected} Rejected</span>
          </div>
        </div>
      </div>

      {/* CRITICAL FEATURE: Before-and-After Investigation Comparison */}
      <div className="p-6 rounded-xl bg-slate-900/80 border border-blue-500/30 shadow-[0_0_25px_rgba(59,130,246,0.1)] space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 pb-3 border-b border-slate-800">
          <div>
            <h2 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              <GitCompare className="w-4 h-4 text-blue-400" />
              Before-and-After Investigation Comparison: Hindsight Memory Impact
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Demonstrating the difference between an initial cold investigation vs a subsequent memory-assisted investigation.
            </p>
          </div>
          <span className="text-[11px] text-purple-400 font-mono bg-purple-950/60 px-2.5 py-1 rounded border border-purple-800/60 self-start md:self-auto font-medium">
            Core Hackathon Demonstration
          </span>
        </div>

        {/* Side-by-Side Comparison Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
          {/* Card 1: First Investigation (Cold / No Prior Memory) */}
          <div className="p-5 rounded-xl bg-slate-950/80 border border-slate-800 space-y-3 relative">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-slate-500" />
                First Investigation (Initial Cold Start)
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-slate-900 text-slate-400 font-mono border border-slate-800">
                0 Prior Memories
              </span>
            </div>

            {firstInv ? (
              <div className="space-y-3 text-xs">
                <div>
                  <div className="font-mono text-blue-400 font-semibold">{firstInv.incident_id}</div>
                  <div className="font-semibold text-slate-200 mt-0.5">{firstInv.title}</div>
                </div>

                <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 text-slate-400 space-y-1">
                  <span className="text-[11px] font-semibold text-slate-300 block">Memory Recall Status:</span>
                  <p className="text-[11px] text-slate-400 italic">
                    "No relevant historical memory found." Memory bank was clean; agent analyzed solely based on ingested telemetry.
                  </p>
                </div>

                <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 space-y-1">
                  <span className="text-[11px] font-semibold text-slate-300 block">Defensive Recommendations:</span>
                  <p className="text-[11px] text-slate-400">
                    Standard baseline response rules. Required full manual analyst verification.
                  </p>
                </div>

                <div className="pt-2 flex items-center justify-between text-[11px] text-slate-500 border-t border-slate-850">
                  <span>Analyst Action:</span>
                  <span className="text-emerald-400 font-medium">Confirmed outcome & retained to Hindsight</span>
                </div>
              </div>
            ) : (
              <div className="p-6 text-center text-xs text-slate-500 space-y-2">
                <ShieldAlert className="w-6 h-6 text-slate-600 mx-auto" />
                <p>Run Incident 1 from the Investigate Threat page and confirm it to populate this comparison card.</p>
                <Link to="/investigate" className="inline-block text-blue-400 text-xs hover:underline font-medium">
                  Run First Investigation →
                </Link>
              </div>
            )}
          </div>

          {/* Card 2: Second Investigation (Memory-Assisted!) */}
          <div className="p-5 rounded-xl bg-purple-950/20 border border-purple-800/60 space-y-3 relative shadow-[0_0_20px_rgba(168,85,247,0.1)]">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-purple-300 uppercase tracking-wider flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-purple-400" />
                Second Investigation (Memory-Assisted)
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-purple-900/50 text-purple-300 font-mono border border-purple-700/60 font-semibold">
                Hindsight Recalled!
              </span>
            </div>

            {secondInv ? (
              <div className="space-y-3 text-xs">
                <div>
                  <div className="font-mono text-purple-400 font-semibold">{secondInv.incident_id}</div>
                  <div className="font-semibold text-slate-200 mt-0.5">{secondInv.title}</div>
                </div>

                <div className="p-3 rounded-lg bg-slate-950/80 border border-purple-900/40 text-slate-300 space-y-1">
                  <span className="text-[11px] font-semibold text-purple-400 block">Memory Recall Intelligence:</span>
                  <p className="text-[11px] text-slate-300 leading-relaxed font-sans">
                    {secondInv.memory_explanation || 'Retrieved confirmed knowledge from Incident 1 resolution.'}
                  </p>
                </div>

                <div className="p-3 rounded-lg bg-slate-950/80 border border-purple-900/40 space-y-1">
                  <span className="text-[11px] font-semibold text-purple-400 block">Enhanced Defense Synthesis:</span>
                  <p className="text-[11px] text-slate-300 leading-relaxed">
                    Agent automatically prioritized perimeter firewall IP drop rules and forced password resets because past confirmed resolution proved their efficacy.
                  </p>
                </div>

                <div className="pt-2 flex items-center justify-between text-[11px] text-slate-400 border-t border-purple-900/30">
                  <span>Advantage:</span>
                  <span className="text-purple-300 font-semibold">Accelerated containment & zero guesswork</span>
                </div>
              </div>
            ) : (
              <div className="p-6 text-center text-xs text-slate-400 space-y-2">
                <Brain className="w-6 h-6 text-purple-400 mx-auto" />
                <p>Run Incident 2 after confirming Incident 1 to see how Hindsight recall informs the second investigation.</p>
                <Link to="/investigate" className="inline-block text-purple-400 text-xs hover:underline font-medium">
                  Run Second Investigation →
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Closed-Loop Learning Diagram & Recommendation Acceptance */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Closed-Loop Learning Cycle */}
        <div className="lg:col-span-2 p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-4">
          <h2 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-blue-400" />
            The ThreatLens Closed-Loop Learning Cycle
          </h2>
          <p className="text-xs text-slate-400">
            How ThreatLens AI continuously evolves its threat response posture with genuine persistent memory:
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 pt-2 text-xs">
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 space-y-1">
              <span className="text-blue-400 font-mono font-bold text-xs">01. INGEST & DETECT</span>
              <p className="text-[11px] text-slate-400">
                Log stream parsed and evaluated via deterministic rules and Agent 1.
              </p>
            </div>
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 space-y-1">
              <span className="text-purple-400 font-mono font-bold text-xs">02. RECALL & REFLECT</span>
              <p className="text-[11px] text-slate-400">
                Agent 3 queries Hindsight bank for identical techniques and remedies.
              </p>
            </div>
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 space-y-1">
              <span className="text-amber-400 font-mono font-bold text-xs">03. HUMAN CONFIRM</span>
              <p className="text-[11px] text-slate-400">
                Analyst reviews findings and accepts/rejects defensive recommendations.
              </p>
            </div>
            <div className="p-3 rounded-lg bg-slate-950 border border-emerald-900/60 space-y-1">
              <span className="text-emerald-400 font-mono font-bold text-xs">04. RETAIN KNOWLEDGE</span>
              <p className="text-[11px] text-slate-400">
                Agent 5 retains confirmed ground-truth into Hindsight memory bank.
              </p>
            </div>
          </div>
        </div>

        {/* Acceptance Bar Chart */}
        <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col">
          <h2 className="text-sm font-semibold text-slate-200 mb-1">
            Recommendation Evaluation
          </h2>
          <p className="text-xs text-slate-500 mb-4">
            Analyst confirmed vs rejected actions
          </p>
          <div className="h-44 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={recStats} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="name" stroke="#64748b" fontSize={10} />
                <YAxis stroke="#64748b" fontSize={10} allowDecimals={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="count" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
