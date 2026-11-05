import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  ShieldAlert,
  Search,
  Filter,
  Brain,
  ArrowUpRight,
  RefreshCw,
  Clock,
  Layers
} from 'lucide-react';
import { getIncidents } from '../api/client';
import SeverityBadge from '../components/SeverityBadge';

export default function Incidents() {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [severityFilter, setSeverityFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  const fetchIncidents = async () => {
    try {
      setLoading(true);
      const data = await getIncidents({
        severity: severityFilter,
        status: statusFilter,
        limit: 100,
      });
      setIncidents(data.incidents || []);
    } catch (err) {
      console.error('Failed to fetch incidents:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncidents();
  }, [severityFilter, statusFilter]);

  const filteredIncidents = incidents.filter((inc) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      inc.incident_id.toLowerCase().includes(q) ||
      inc.title.toLowerCase().includes(q) ||
      (inc.attack_type && inc.attack_type.toLowerCase().includes(q))
    );
  });

  return (
    <div className="space-y-6">
      {/* Title & Filters */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight flex items-center gap-2">
            Incident Repository
            <span className="text-xs px-2 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30 font-normal">
              {filteredIncidents.length} Records
            </span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Complete archive of investigated threat events, evidence timelines, and confirmed analyst resolutions.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={fetchIncidents}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <Link
            to="/investigate"
            className="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-[0_0_12px_rgba(59,130,246,0.3)] transition"
          >
            New Investigation
          </Link>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col md:flex-row gap-4 items-center justify-between">
        {/* Search */}
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search by ID, title, or attack type..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 rounded-lg bg-slate-950 border border-slate-700 text-xs text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-blue-500"
          />
        </div>

        {/* Filters */}
        <div className="flex items-center gap-3 w-full md:w-auto">
          <div className="flex items-center gap-1.5 text-xs text-slate-400">
            <Filter className="w-3.5 h-3.5" />
            <span>Severity:</span>
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1 text-xs text-slate-300 focus:outline-none focus:border-blue-500"
            >
              <option value="all">All Severities</option>
              <option value="Critical">Critical</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>
          </div>

          <div className="flex items-center gap-1.5 text-xs text-slate-400">
            <span>Status:</span>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1 text-xs text-slate-300 focus:outline-none focus:border-blue-500"
            >
              <option value="all">All Statuses</option>
              <option value="open">Open</option>
              <option value="confirmed">Confirmed</option>
              <option value="resolved">Resolved</option>
            </select>
          </div>
        </div>
      </div>

      {/* Incidents Table */}
      <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800">
        {loading ? (
          <div className="p-12 text-center text-xs text-slate-400">
            <RefreshCw className="w-6 h-6 text-blue-400 animate-spin mx-auto mb-2" />
            Loading incidents...
          </div>
        ) : filteredIncidents.length === 0 ? (
          <div className="p-12 text-center text-xs text-slate-500">
            No incidents matched your criteria.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/60 text-slate-400 border-b border-slate-800 uppercase tracking-wider font-mono text-[10px]">
                <tr>
                  <th className="py-2.5 px-3">Incident ID</th>
                  <th className="py-2.5 px-3">Title / Attack Pattern</th>
                  <th className="py-2.5 px-3">Severity</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3">Events</th>
                  <th className="py-2.5 px-3">Hindsight Memory</th>
                  <th className="py-2.5 px-3">Date & Time</th>
                  <th className="py-2.5 px-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {filteredIncidents.map((inc) => (
                  <tr key={inc.incident_id} className="hover:bg-slate-800/30 transition">
                    <td className="py-3 px-3 font-mono font-medium text-blue-400">
                      <Link to={`/incidents/${inc.incident_id}`} className="hover:underline">
                        {inc.incident_id}
                      </Link>
                    </td>
                    <td className="py-3 px-3 font-medium text-slate-200">
                      <div>{inc.title}</div>
                      <div className="text-[11px] text-slate-500 font-normal">
                        {inc.attack_type}
                      </div>
                    </td>
                    <td className="py-3 px-3">
                      <SeverityBadge severity={inc.severity} />
                    </td>
                    <td className="py-3 px-3">
                      <span className={`capitalize font-mono text-[11px] px-2 py-0.5 rounded border ${
                        inc.status === 'confirmed'
                          ? 'bg-emerald-950/50 text-emerald-400 border-emerald-800/50'
                          : 'bg-slate-950 text-slate-400 border-slate-800'
                      }`}>
                        {inc.status || 'open'}
                      </span>
                    </td>
                    <td className="py-3 px-3 font-mono text-slate-400 text-[11px]">
                      {inc.event_count || inc.timeline?.length || 0}
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
                      {inc.created_at ? new Date(inc.created_at).toLocaleString() : 'N/A'}
                    </td>
                    <td className="py-3 px-3 text-right">
                      <Link
                        to={`/incidents/${inc.incident_id}`}
                        className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition font-medium"
                      >
                        Details
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
