import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  ShieldAlert,
  AlertTriangle,
  AlertCircle,
  CheckCircle2,
  Brain,
  Activity,
  ArrowUpRight,
  FileText,
  Clock,
  Sparkles,
  RefreshCw,
  Database,
  Check,
  X,
  Layers,
  ChevronRight
} from 'lucide-react';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid
} from 'recharts';
import { getAnalytics, getIncidents, getHealth } from '../api/client';
import SeverityBadge from '../components/SeverityBadge';
import AgentStatusBadge from '../components/AgentStatusBadge';

export default function Overview() {
  const [analytics, setAnalytics] = useState(null);
  const [recentIncidents, setRecentIncidents] = useState([]);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setErrorMsg(null);
      const [analyticsData, incidentsData, healthData] = await Promise.all([
        getAnalytics(),
        getIncidents({ limit: 6 }),
        getHealth()
      ]);
      setAnalytics(analyticsData);
      setRecentIncidents(incidentsData.incidents || []);
      setHealth(healthData);
    } catch (err) {
      console.error('Failed to load overview data:', err);
      setErrorMsg(
        err.response?.data?.detail ||
        'Unable to connect to ThreatLens AI backend or MongoDB. Verify services are operational.'
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Real backend metrics (guaranteed 0 if empty, no placeholders)
  const metrics = analytics?.metrics || {
    total_incidents: 0,
    critical_count: 0,
    high_count: 0,
    medium_count: 0,
    low_count: 0,
    confirmed_count: 0,
    memory_recalled_count: 0,
    memory_retained_count: 0,
    total_recommendations: 0,
    total_recommendations_accepted: 0,
    total_recommendations_rejected: 0,
    total_recommendations_pending: 0,
    total_recommendations_reviewed: 0,
    acceptance_rate: null,
    acceptance_rate_display: 'N/A'
  };

  // Severity data strictly derived from real database counts
  const severityData = [
    { name: 'Critical', value: metrics.critical_count || 0, color: '#ef4444' },
    { name: 'High', value: metrics.high_count || 0, color: '#f97316' },
    { name: 'Medium', value: metrics.medium_count || 0, color: '#eab308' },
    { name: 'Low', value: metrics.low_count || 0, color: '#10b981' },
  ];

  // Real incident activity timeline
  const activityData = (analytics?.activity_timeline || []).map((item) => ({
    id: item.id,
    name: item.name || item.id,
    fullId: item.full_id || item.id,
    title: item.title,
    date: item.date,
    time: item.time,
    severity: item.severity,
    recommendations: typeof item.recommendations_count === 'number' ? item.recommendations_count : 0,
    memoryUsed: item.memory_used ? 1 : 0,
    hindsightStatus: item.hindsight_status,
  }));

  // Real agent mesh status
  const agentMesh = analytics?.agent_mesh || [
    { id: 'detection', name: 'Threat Detection Agent', role: 'Rule execution & log pattern analysis', status: health?.agents?.agent_1_detection || 'available' },
    { id: 'investigation', name: 'Investigation Agent', role: 'Timeline creation & hypothesis testing', status: health?.agents?.agent_2_investigation || 'available' },
    { id: 'memory', name: 'Hindsight Memory Agent', role: 'Recall & reflect across memory bank', status: health?.agents?.agent_3_memory || 'available' },
    { id: 'response', name: 'Response Recommendation Agent', role: 'Defensive recommendations formulation', status: health?.agents?.agent_4_response || 'available' },
    { id: 'learning', name: 'Learning Agent', role: 'Durable knowledge retention post-review', status: health?.agents?.agent_5_learning || 'available' },
  ];

  // Custom Tooltip for Activity Chart
  const CustomBarTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="p-3 rounded-lg bg-slate-950 border border-slate-700 text-xs shadow-xl space-y-1 max-w-xs">
          <div className="flex items-center justify-between gap-2 border-b border-slate-800 pb-1.5 font-mono">
            <span className="font-semibold text-blue-400">{data.fullId}</span>
            <SeverityBadge severity={data.severity} />
          </div>
          <p className="text-slate-200 font-medium text-[11px] truncate pt-0.5">{data.title}</p>
          <div className="flex items-center justify-between text-slate-400 text-[11px] pt-1">
            <span>Defensive Actions:</span>
            <span className="font-mono font-semibold text-slate-100">{data.recommendations}</span>
          </div>
          <div className="flex items-center justify-between text-slate-400 text-[11px]">
            <span>Hindsight Recall:</span>
            <span className={`font-mono text-[10px] ${data.memoryUsed ? 'text-purple-400 font-semibold' : 'text-slate-500'}`}>
              {data.memoryUsed ? 'Recalled' : 'None'}
            </span>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-6">
      {/* Page Title & Refresh */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight flex items-center gap-2">
            SOC Intelligence Overview
            <span className="text-xs px-2 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30 font-normal">
              Live Monitoring
            </span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time multi-agent detection, persistent incident recall, and autonomous defensive synthesis.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchData}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 transition disabled:opacity-50"
            title="Fetch fresh live data from MongoDB and Hindsight"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <Link
            to="/investigate"
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-[0_0_12px_rgba(59,130,246,0.3)] transition"
          >
            Launch Investigation
          </Link>
        </div>
      </div>

      {/* Backend / Database Connection Status Banner */}
      {errorMsg ? (
        <div className="p-4 rounded-xl bg-red-950/70 border border-red-800 text-red-200 text-xs flex items-center justify-between gap-3 shadow-lg">
          <div className="flex items-center gap-2.5">
            <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
            <span>{errorMsg}</span>
          </div>
          <button
            onClick={fetchData}
            className="px-2.5 py-1 rounded bg-red-900/60 hover:bg-red-800 text-white text-[11px] font-semibold border border-red-700"
          >
            Retry Connection
          </button>
        </div>
      ) : (
        <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-wrap items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-4">
            {/* MongoDB */}
            <div className="flex items-center gap-2">
              <Database className="w-3.5 h-3.5 text-blue-400" />
              <span className="text-slate-400">Database:</span>
              <span className="font-mono font-semibold text-slate-200">
                {health?.mongodb?.status === 'connected' ? 'MongoDB Active' : 'Connecting...'}
              </span>
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            </div>

            {/* Hindsight Bank */}
            <div className="flex items-center gap-2 border-l border-slate-800 pl-4">
              <Brain className="w-3.5 h-3.5 text-purple-400" />
              <span className="text-slate-400">Memory Bank:</span>
              <span className="font-mono font-semibold text-slate-200">
                {health?.hindsight?.status === 'connected' ? 'Hindsight Cloud Connected' : 'Checking...'}
              </span>
              <span className="w-1.5 h-1.5 rounded-full bg-purple-400 animate-pulse" />
            </div>
          </div>

          <div className="text-[11px] text-slate-500 font-mono">
            {metrics.total_incidents} incident record(s) persisted in MongoDB
          </div>
        </div>
      )}

      {/* Top 4 Real Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Total Investigated */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 backdrop-blur relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-2">
            <span>Total Investigated</span>
            <FileText className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-3xl font-bold text-slate-100 font-mono">
            {loading && !analytics ? '...' : metrics.total_incidents}
          </div>
          <div className="mt-2 flex items-center justify-between text-[11px] text-slate-400 pt-1 border-t border-slate-800/60">
            <span>Analyst Confirmed:</span>
            <span className="font-semibold text-slate-200 font-mono">{metrics.confirmed_count}</span>
          </div>
          <div className="absolute top-0 right-0 w-24 h-24 bg-blue-500/5 rounded-full blur-xl pointer-events-none" />
        </div>

        {/* Card 2: Threat Severity */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-red-900/30 backdrop-blur relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-2">
            <span className="text-red-300 font-medium">Critical Threats</span>
            <ShieldAlert className="w-4 h-4 text-red-400" />
          </div>
          <div className="text-3xl font-bold text-red-400 font-mono">
            {loading && !analytics ? '...' : metrics.critical_count}
          </div>
          <div className="mt-2 flex items-center justify-between text-[11px] text-slate-400 pt-1 border-t border-slate-800/60 font-mono">
            <span>High: <strong className="text-orange-400 font-semibold">{metrics.high_count}</strong></span>
            <span>Med: <strong className="text-yellow-400 font-semibold">{metrics.medium_count}</strong></span>
            <span>Low: <strong className="text-emerald-400 font-semibold">{metrics.low_count}</strong></span>
          </div>
          <div className="absolute top-0 right-0 w-24 h-24 bg-red-500/10 rounded-full blur-xl pointer-events-none" />
        </div>

        {/* Card 3: Memory Recalled & Retained */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-purple-900/30 backdrop-blur relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-2">
            <span className="text-purple-300 font-medium">Memory Recalled</span>
            <Brain className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-3xl font-bold text-purple-400 font-mono">
            {loading && !analytics ? '...' : metrics.memory_recalled_count}
          </div>
          <div className="mt-2 flex items-center justify-between text-[11px] text-slate-400 pt-1 border-t border-slate-800/60">
            <span>Memories Retained:</span>
            <span className="font-semibold text-purple-300 font-mono">{metrics.memory_retained_count}</span>
          </div>
          <div className="absolute top-0 right-0 w-24 h-24 bg-purple-500/10 rounded-full blur-xl pointer-events-none" />
        </div>

        {/* Card 4: Acceptance Rate & Defensive Actions */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-emerald-900/30 backdrop-blur relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-2">
            <span className="text-emerald-300 font-medium">Acceptance Rate</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-3xl font-bold font-mono">
            {loading && !analytics ? (
              <span className="text-slate-400">...</span>
            ) : metrics.acceptance_rate !== null ? (
              <span className="text-emerald-400">{metrics.acceptance_rate}%</span>
            ) : (
              <span className="text-slate-500 text-2xl">N/A</span>
            )}
          </div>
          <div className="mt-2 flex items-center justify-between text-[11px] text-slate-400 pt-1 border-t border-slate-800/60 font-mono">
            <span>Accepted: <strong className="text-emerald-400 font-semibold">{metrics.total_recommendations_accepted}</strong></span>
            <span>Rej: <strong className="text-red-400 font-semibold">{metrics.total_recommendations_rejected}</strong></span>
            <span>Pending: <strong className="text-slate-300 font-semibold">{metrics.total_recommendations_pending}</strong></span>
          </div>
          <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/10 rounded-full blur-xl pointer-events-none" />
        </div>
      </div>

      {/* Multi-Agent Status Grid (Reflecting actual backend readiness) */}
      <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
            <Activity className="w-4 h-4 text-blue-400" />
            Active SOC Multi-Agent Mesh
          </h2>
          <span className="text-[11px] text-slate-500 font-mono">
            Live Health Verification • 5 Specialized Agents
          </span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
          {agentMesh.map((agent) => (
            <AgentStatusBadge
              key={agent.id}
              agentName={agent.id}
              customLabel={agent.name}
              role={agent.role}
              status={agent.status}
              executionCount={agent.execution_count}
            />
          ))}
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Severity Distribution Pie Chart */}
        <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-slate-200">Threat Severity Distribution</h2>
            <span className="text-[11px] text-slate-500 font-mono">Actual Log Findings</span>
          </div>
          <div className="h-48 w-full flex items-center justify-center">
            {metrics.total_incidents === 0 ? (
              <div className="p-6 text-center text-xs text-slate-500 bg-slate-950/40 rounded-lg border border-dashed border-slate-800 w-full">
                <ShieldAlert className="w-6 h-6 text-slate-600 mx-auto mb-1.5 opacity-60" />
                No security incidents recorded yet.<br />
                <span className="text-[11px] text-slate-600 mt-1 block">
                  Run an investigation to visualize threat severity.
                </span>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={severityData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={45}
                    outerRadius={75}
                    paddingAngle={4}
                  >
                    {severityData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: '#020617', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                    itemStyle={{ color: '#e2e8f0' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
          <div className="grid grid-cols-2 gap-2 mt-4 pt-3 border-t border-slate-800 text-xs">
            {severityData.map((s) => (
              <div key={s.name} className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-sm" style={{ backgroundColor: s.color }} />
                <span className="text-slate-400">{s.name}:</span>
                <span className="font-mono font-semibold text-slate-200">{s.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Activity & Defensive Actions Bar Chart */}
        <div className="lg:col-span-2 p-5 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-semibold text-slate-200">Incident Activity & Defensive Actions</h2>
              <p className="text-xs text-slate-500">Defensive recommendations generated per incident stream</p>
            </div>
            <span className="text-[11px] text-blue-400 font-mono bg-blue-950/40 px-2 py-0.5 rounded border border-blue-900/40">
              {metrics.total_recommendations} Total Actions Formulated
            </span>
          </div>
          <div className="h-56 w-full">
            {activityData.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center p-6 text-center text-xs text-slate-500 bg-slate-950/40 rounded-lg border border-dashed border-slate-800">
                <Layers className="w-7 h-7 text-slate-600 mb-2 opacity-50" />
                <span>No incident streams recorded.</span>
                <span className="text-[11px] text-slate-600 mt-0.5">
                  Investigations and generated defensive actions will plot here.
                </span>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={activityData} margin={{ top: 10, right: 15, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} />
                  <YAxis stroke="#64748b" fontSize={11} allowDecimals={false} tickLine={false} />
                  <Tooltip content={<CustomBarTooltip />} />
                  <Bar
                    dataKey="recommendations"
                    name="Defensive Actions"
                    fill="#3b82f6"
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>

      {/* Recent Investigations Table */}
      <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-sm font-semibold text-slate-200">Recent Threat Investigations</h2>
            <p className="text-xs text-slate-500">Latest multi-agent investigations with evidence & recommendations</p>
          </div>
          <Link
            to="/incidents"
            className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1 font-medium transition"
          >
            View all incidents <ArrowUpRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {recentIncidents.length === 0 ? (
          <div className="p-8 text-center rounded-lg bg-slate-950/40 border border-dashed border-slate-800">
            <FileText className="w-8 h-8 text-slate-600 mx-auto mb-2" />
            <h3 className="text-sm font-medium text-slate-400">No threat investigations yet</h3>
            <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
              Upload your security logs or load a sample cybersecurity attack dataset to run your first multi-agent investigation.
            </p>
            <Link
              to="/investigate"
              className="mt-4 inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold transition"
            >
              Start Investigation
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/60 text-slate-400 border-b border-slate-800 uppercase tracking-wider font-mono text-[10px]">
                <tr>
                  <th className="py-2.5 px-3">Incident ID</th>
                  <th className="py-2.5 px-3">Attack Classification</th>
                  <th className="py-2.5 px-3">Severity</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3">Hindsight Memory</th>
                  <th className="py-2.5 px-3">Created</th>
                  <th className="py-2.5 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {recentIncidents.map((inc) => (
                  <tr key={inc.incident_id} className="hover:bg-slate-800/30 transition">
                    <td className="py-3 px-3 font-mono font-medium text-blue-400">
                      <Link to={`/incidents/${inc.incident_id}`} className="hover:underline">
                        {inc.incident_id}
                      </Link>
                    </td>
                    <td className="py-3 px-3 font-medium text-slate-200">
                      {inc.attack_type || inc.title}
                    </td>
                    <td className="py-3 px-3">
                      <SeverityBadge severity={inc.severity} />
                    </td>
                    <td className="py-3 px-3">
                      <span className="capitalize text-slate-400 font-mono text-[11px]">
                        {inc.status || 'open'}
                      </span>
                    </td>
                    <td className="py-3 px-3">
                      {inc.memory_used ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] bg-purple-950/60 text-purple-400 border border-purple-800/60 font-medium">
                          <Brain className="w-3 h-3" /> Recalled
                        </span>
                      ) : (
                        <span className="text-slate-500 text-[11px]">None</span>
                      )}
                    </td>
                    <td className="py-3 px-3 text-slate-500 font-mono text-[11px]">
                      {inc.created_at ? new Date(inc.created_at).toLocaleTimeString() : 'Recent'}
                    </td>
                    <td className="py-3 px-3 text-right">
                      <Link
                        to={`/incidents/${inc.incident_id}`}
                        className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition font-medium inline-flex items-center gap-1"
                      >
                        Inspect <ChevronRight className="w-3 h-3" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
