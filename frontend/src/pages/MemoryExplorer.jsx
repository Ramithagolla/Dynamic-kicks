import React, { useState, useEffect } from 'react';
import {
  Brain,
  Search,
  Sparkles,
  Database,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Layers,
  FileText,
  Tag,
  Clock,
  ArrowRight
} from 'lucide-react';
import { searchMemory, reflectMemory, getMemoryHealth, listRecentMemories } from '../api/client';

const SAMPLE_QUERIES = [
  'Credential stuffing password spray resolution',
  'Brute force SSH unauthorized login containment',
  '198.51.100.42 perimeter firewall block',
  'admin_sarah session token revocation',
];

export default function MemoryExplorer() {
  const [query, setQuery] = useState('Credential stuffing password spray resolution');
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchResults, setSearchResults] = useState(null);
  const [health, setHealth] = useState(null);

  // Reflect sandbox state
  const [reflectQuery, setReflectQuery] = useState('What containment actions are proven effective against credential stuffing?');
  const [reflectContext, setReflectContext] = useState('Observed repeated failed logins followed by successful admin logon from external IP.');
  const [reflectLoading, setReflectLoading] = useState(false);
  const [reflectResult, setReflectResult] = useState(null);

  const fetchHealth = async () => {
    try {
      const data = await getMemoryHealth();
      setHealth(data);
    } catch (err) {
      console.error('Failed to get memory health:', err);
    }
  };

  useEffect(() => {
    fetchHealth();
    handleSearch();
  }, []);

  const handleSearch = async (queryToSearch = query) => {
    if (!queryToSearch.trim()) return;
    setSearchLoading(true);
    try {
      const res = await searchMemory(queryToSearch.trim());
      setSearchResults(res);
    } catch (err) {
      setSearchResults({
        success: false,
        error: err.response?.data?.detail || 'Hindsight recall failed',
        results: [],
        count: 0,
      });
    } finally {
      setSearchLoading(false);
    }
  };

  const handleReflect = async () => {
    if (!reflectQuery.trim()) return;
    setReflectLoading(true);
    try {
      const res = await reflectMemory(reflectQuery.trim(), reflectContext.trim());
      setReflectResult(res);
    } catch (err) {
      setReflectResult({
        success: false,
        error: err.response?.data?.detail || 'Hindsight reflect failed',
      });
    } finally {
      setReflectLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold text-slate-100 tracking-tight flex items-center gap-2">
          Hindsight Persistent Memory Explorer
          <span className="text-xs px-2 py-0.5 rounded bg-purple-500/20 text-purple-400 border border-purple-500/30 font-normal">
            Semantic Intelligence
          </span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Direct semantic search, graph traversal, and reflection across the <code className="text-purple-300 font-mono">threatlens-security-memory</code> persistent memory bank.
        </p>
      </div>

      {/* Memory Bank Health Card */}
      <div className="p-5 rounded-xl bg-slate-900/60 border border-purple-900/40 relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-purple-950/80 border border-purple-700/60 flex items-center justify-center text-purple-400">
              <Brain className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-semibold text-slate-200 text-sm">
                  Shared Memory Bank:
                </span>
                <span className="font-mono text-purple-300 text-xs font-bold bg-purple-950/60 px-2 py-0.5 rounded border border-purple-800/60">
                  {health?.bank_id || 'threatlens-security-memory'}
                </span>
              </div>
              <div className="text-xs text-slate-400 mt-0.5">
                Endpoint: <span className="font-mono text-slate-300 text-[11px]">{health?.base_url || 'https://api.hindsight.vectorize.io'}</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="text-right">
              <div className="text-[11px] text-slate-400">Connection Status</div>
              <div className="text-xs font-semibold capitalize flex items-center gap-1.5 justify-end">
                <span
                  className={`w-2 h-2 rounded-full ${
                    health?.status === 'connected' ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'
                  }`}
                />
                <span className="text-slate-200">{health?.status || 'Active'}</span>
              </div>
            </div>

            <button
              onClick={fetchHealth}
              className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-xs transition"
              title="Refresh Hindsight Health"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {health?.last_error && (
          <div className="mt-3 pt-3 border-t border-purple-900/30 text-[11px] text-amber-300/80 font-mono">
            Notice: {health.last_error}
          </div>
        )}
      </div>

      {/* Recall / Search Workbench */}
      <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
            <Search className="w-4 h-4 text-blue-400" />
            Hindsight Recall (Semantic & Temporal Multi-Dimensional Retrieval)
          </h2>
          <span className="text-xs text-slate-500 font-mono">
            Operation: recall
          </span>
        </div>

        {/* Search Bar */}
        <div className="flex flex-col sm:flex-row gap-2">
          <div className="relative flex-1">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Query memory bank by attack pattern, IOC, or mitigation..."
              className="w-full px-4 py-2.5 rounded-lg bg-slate-950 border border-slate-700 text-xs text-slate-200 font-medium focus:outline-none focus:border-blue-500"
            />
          </div>
          <button
            onClick={() => handleSearch()}
            disabled={searchLoading}
            className="px-5 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs flex items-center justify-center gap-2 transition shadow-[0_0_15px_rgba(59,130,246,0.25)] shrink-0 disabled:opacity-50"
          >
            {searchLoading ? (
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Search className="w-3.5 h-3.5" />
            )}
            Recall Memory
          </button>
        </div>

        {/* Query Suggestion Chips */}
        <div className="flex flex-wrap items-center gap-2 pt-1">
          <span className="text-[11px] text-slate-500 font-medium">Quick Queries:</span>
          {SAMPLE_QUERIES.map((sq, idx) => (
            <button
              key={idx}
              onClick={() => {
                setQuery(sq);
                handleSearch(sq);
              }}
              className="text-[11px] px-2.5 py-1 rounded-md bg-slate-950 text-slate-400 hover:text-slate-200 hover:bg-slate-800 border border-slate-800 transition"
            >
              {sq}
            </button>
          ))}
        </div>

        {/* Search Results Display */}
        {searchResults && (
          <div className="mt-4 pt-4 border-t border-slate-800 space-y-3">
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-400">
                Retrieved Results: <span className="font-semibold text-slate-200 font-mono">{searchResults.count || 0}</span>
              </span>
              <span className="text-[11px] text-slate-500 font-mono">
                Query: "{searchResults.query}"
              </span>
            </div>

            {searchResults.count === 0 ? (
              <div className="p-8 text-center rounded-lg bg-slate-950/60 border border-dashed border-slate-800">
                <Brain className="w-6 h-6 text-slate-600 mx-auto mb-2" />
                <div className="text-xs font-medium text-slate-400">
                  {searchResults.message || 'No relevant historical memory found.'}
                </div>
                <p className="text-[11px] text-slate-500 mt-1 max-w-md mx-auto">
                  Confirm an incident resolution on the Incident Details page to retain memories into the bank. Subsequent queries will retrieve them immediately.
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {searchResults.results.map((item, idx) => (
                  <div
                    key={item.id || idx}
                    className="p-4 rounded-lg bg-slate-950/80 border border-purple-900/40 text-xs space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-purple-400 font-semibold text-[11px]">
                        ID: {item.document_id || item.id || `memory-${idx + 1}`}
                      </span>
                      {item.type && (
                        <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-800">
                          {item.type}
                        </span>
                      )}
                    </div>
                    <p className="text-slate-200 font-mono text-[11px] whitespace-pre-line leading-relaxed">
                      {item.text}
                    </p>
                    {item.tags && item.tags.length > 0 && (
                      <div className="flex items-center gap-1.5 pt-1">
                        <Tag className="w-3 h-3 text-slate-500" />
                        {item.tags.map((t, tIdx) => (
                          <span
                            key={tIdx}
                            className="text-[10px] font-mono text-slate-400 bg-slate-900 px-1.5 py-0.2 rounded"
                          >
                            #{t}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Reflect Sandbox */}
      <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-purple-400" />
            Hindsight Reflection (Cognitive Reasoning Over Memory)
          </h2>
          <span className="text-xs text-purple-400 font-mono">
            Operation: reflect
          </span>
        </div>

        <p className="text-xs text-slate-400">
          Unlike flat keyword search, reflection reasons across accumulated incident memories, extracting proven defense tactics, tracking lessons learned, and synthesizing tailored mitigation guidance.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-[11px] font-semibold text-slate-400 uppercase mb-1">
              Reflection Query
            </label>
            <input
              type="text"
              value={reflectQuery}
              onChange={(e) => setReflectQuery(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-purple-500"
            />
          </div>
          <div>
            <label className="block text-[11px] font-semibold text-slate-400 uppercase mb-1">
              Incident Context (Optional)
            </label>
            <input
              type="text"
              value={reflectContext}
              onChange={(e) => setReflectContext(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-purple-500"
            />
          </div>
        </div>

        <button
          onClick={handleReflect}
          disabled={reflectLoading}
          className="px-5 py-2 rounded-lg bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs flex items-center gap-2 transition shadow-[0_0_15px_rgba(168,85,247,0.25)] disabled:opacity-50"
        >
          {reflectLoading ? (
            <RefreshCw className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <Sparkles className="w-3.5 h-3.5" />
          )}
          Execute Hindsight Reflection
        </button>

        {reflectResult && (
          <div className="mt-4 p-4 rounded-lg bg-purple-950/30 border border-purple-800/60 space-y-2">
            <span className="text-xs font-semibold text-purple-300 block">
              Synthesized Reflection Output:
            </span>
            <div className="text-xs text-slate-200 leading-relaxed font-sans">
              {reflectResult.synthesis || reflectResult.error || 'No reflection response generated.'}
            </div>

            {reflectResult.based_on && reflectResult.based_on.length > 0 && (
              <div className="mt-3 pt-3 border-t border-purple-900/40 text-[11px] space-y-1">
                <span className="text-slate-400 font-semibold">Grounded on Historical Facts ({reflectResult.based_on.length}):</span>
                {reflectResult.based_on.map((fact, fIdx) => (
                  <div key={fIdx} className="text-slate-400 font-mono">
                    • {fact.text}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
