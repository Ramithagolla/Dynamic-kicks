import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ShieldAlert,
  ArrowLeft,
  Clock,
  Brain,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  FileText,
  ListOrdered,
  Cpu,
  Sparkles,
  Lock,
  Layers,
  Send,
  ExternalLink
} from 'lucide-react';
import { getIncidentById, submitFeedback } from '../api/client';
import SeverityBadge from '../components/SeverityBadge';

export default function IncidentDetails() {
  const { incidentId } = useParams();
  const [incident, setIncident] = useState(null);
  const [events, setEvents] = useState([]);
  const [feedback, setFeedback] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submittingFeedback, setSubmittingFeedback] = useState(false);
  const [feedbackStatus, setFeedbackStatus] = useState(null);

  // Analyst feedback form state
  const [findingConfirmed, setFindingConfirmed] = useState(true);
  const [confirmedRootCause, setConfirmedRootCause] = useState('');
  const [resolutionNotes, setResolutionNotes] = useState('');
  const [acceptedRecs, setAcceptedRecs] = useState({});

  const fetchIncident = async () => {
    try {
      setLoading(true);
      const data = await getIncidentById(incidentId);
      setIncident(data.incident);
      setEvents(data.events || []);
      setFeedback(data.feedback);

      // Initialize form defaults if not yet confirmed
      if (data.incident) {
        setConfirmedRootCause(
          data.feedback?.confirmed_root_cause ||
          `Adversary exploited weak credentials via ${data.incident.attack_type}`
        );
        setResolutionNotes(
          data.feedback?.resolution_notes ||
          `Perimeter IP drop list rule applied. Account password reset and token revocation enforced.`
        );

        // Default all recommendations to accepted
        const recMap = {};
        (data.incident.recommendations || []).forEach((r) => {
          recMap[r.action] = data.feedback?.accepted_recommendations
            ? data.feedback.accepted_recommendations.includes(r.action)
            : true;
        });
        setAcceptedRecs(recMap);
      }
    } catch (err) {
      console.error('Failed to load incident details:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncident();
  }, [incidentId]);

  const toggleRec = (actionName) => {
    setAcceptedRecs((prev) => ({
      ...prev,
      [actionName]: !prev[actionName],
    }));
  };

  const handleFeedbackSubmit = async (e) => {
    e.preventDefault();
    setSubmittingFeedback(true);
    setFeedbackStatus(null);

    const acceptedList = Object.keys(acceptedRecs).filter((k) => acceptedRecs[k]);
    const rejectedList = Object.keys(acceptedRecs).filter((k) => !acceptedRecs[k]);

    const payload = {
      finding_confirmed: findingConfirmed,
      accepted_recommendations: acceptedList,
      rejected_recommendations: rejectedList,
      confirmed_root_cause: confirmedRootCause,
      resolution_notes: resolutionNotes,
    };

    try {
      const res = await submitFeedback(incidentId, payload);
      setFeedbackStatus({
        type: 'success',
        retentionStatus: res.retention_status,
        details: res.hindsight_retention,
        message: res.hindsight_retention?.details?.message || res.message,
      });
      // Refresh to get updated status
      await fetchIncident();
    } catch (err) {
      setFeedbackStatus({
        type: 'error',
        message: err.response?.data?.detail || 'Failed to submit analyst confirmation.',
      });
    } finally {
      setSubmittingFeedback(false);
    }
  };

  if (loading) {
    return (
      <div className="p-16 text-center text-xs text-slate-400">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
        Retrieving incident telemetry and Hindsight knowledge...
      </div>
    );
  }

  if (!incident) {
    return (
      <div className="p-8 text-center bg-slate-900/60 rounded-xl border border-slate-800">
        <h2 className="text-sm font-semibold text-slate-200">Incident Not Found</h2>
        <p className="text-xs text-slate-500 mt-1">Incident ID {incidentId} was not found in the database.</p>
        <Link to="/incidents" className="mt-4 inline-block text-xs text-blue-400 hover:underline">
          Return to Incident Repository
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Top Breadcrumb & Action Bar */}
      <div className="flex items-center justify-between">
        <Link
          to="/incidents"
          className="text-xs text-slate-400 hover:text-slate-200 flex items-center gap-1.5 transition font-medium"
        >
          <ArrowLeft className="w-3.5 h-3.5" /> Back to Incidents
        </Link>
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400 font-mono">
            {new Date(incident.created_at).toLocaleString()}
          </span>
        </div>
      </div>

      {/* Incident Header Card */}
      <div className="p-6 rounded-xl bg-slate-900/80 border border-slate-800 shadow-lg relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="font-mono text-xs font-bold text-blue-400 bg-blue-950/60 px-2 py-0.5 rounded border border-blue-800/60">
                {incident.incident_id}
              </span>
              <SeverityBadge severity={incident.severity} />
              <span className={`text-[11px] font-mono capitalize px-2 py-0.5 rounded border ${
                incident.status === 'confirmed'
                  ? 'bg-emerald-950/50 text-emerald-400 border-emerald-800/50'
                  : 'bg-slate-950 text-slate-400 border-slate-800'
              }`}>
                {incident.status}
              </span>
              {incident.memory_used && (
                <span className="px-2 py-0.5 rounded text-[11px] bg-purple-950/60 text-purple-400 border border-purple-800 flex items-center gap-1 font-medium">
                  <Brain className="w-3 h-3" /> Hindsight Recalled
                </span>
              )}
            </div>
            <h1 className="text-xl font-bold text-slate-100 tracking-tight">
              {incident.title}
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Attack Classification: <span className="text-slate-200 font-semibold">{incident.attack_type}</span>
            </p>
          </div>
        </div>

        {/* Indicators Bar */}
        {incident.indicators && incident.indicators.length > 0 && (
          <div className="mt-4 pt-3 border-t border-slate-800/80 flex flex-wrap items-center gap-2">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
              Indicators (IOCs):
            </span>
            {incident.indicators.map((ind, idx) => (
              <span
                key={idx}
                className="px-2 py-0.5 rounded bg-slate-950 text-slate-300 font-mono text-[11px] border border-slate-800"
              >
                {ind}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Main Grid: Left 2 Cols Findings & Timeline, Right Col Memory & Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols */}
        <div className="lg:col-span-2 space-y-6">
          {/* Section: Investigation Summary & Findings */}
          <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-4">
            <h2 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
              <FileText className="w-4 h-4 text-blue-400" />
              Investigation Narrative & Evidence-Backed Findings
            </h2>
            <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/80 p-3 rounded-lg border border-slate-850">
              {incident.response_summary || incident.title}
            </p>

            {/* Findings List */}
            <div className="space-y-3">
              {(incident.findings || []).map((finding, idx) => (
                <div
                  key={idx}
                  className="p-3.5 rounded-lg bg-slate-950/60 border border-slate-800/80 text-xs space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-200 flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />
                      {finding.title}
                    </span>
                    <span className="text-[10px] font-mono text-blue-400 bg-blue-950/40 px-2 py-0.5 rounded border border-blue-900/40">
                      {Math.round((finding.confidence || 0.95) * 100)}% Confidence
                    </span>
                  </div>
                  <p className="text-slate-400">{finding.description}</p>
                  {finding.evidence && finding.evidence.length > 0 && (
                    <div className="mt-2 bg-slate-900/50 p-2 rounded text-[11px] text-slate-400 font-mono space-y-1">
                      <div className="text-[10px] text-slate-500 uppercase font-semibold">Supporting Evidence:</div>
                      {finding.evidence.map((ev, eIdx) => (
                        <div key={eIdx}>• {ev}</div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Section: Separated Facts vs Hypotheses vs Limitations */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Observed Facts */}
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
              <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                Confirmed Observed Facts
              </h3>
              <ul className="text-xs text-slate-400 space-y-1.5 list-disc list-inside">
                {(incident.observed_facts || []).map((fact, idx) => (
                  <li key={idx} className="leading-relaxed">{fact}</li>
                ))}
              </ul>
            </div>

            {/* Hypotheses */}
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
              <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                Analyst Hypotheses (Unverified)
              </h3>
              <ul className="text-xs text-slate-400 space-y-1.5 list-disc list-inside">
                {(incident.hypotheses || []).map((hypo, idx) => (
                  <li key={idx} className="leading-relaxed">{hypo}</li>
                ))}
              </ul>
            </div>
          </div>

          {/* Chronological Event Timeline */}
          <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
            <h2 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
              <Clock className="w-4 h-4 text-blue-400" />
              Chronological Security Event Timeline ({events.length} Telemetry Events)
            </h2>

            <div className="relative pl-6 space-y-4 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
              {events.map((ev, idx) => {
                const isFailed = ev.status === 'failed';
                const isSuccess = ev.status === 'success';

                return (
                  <div key={ev.event_id || idx} className="relative text-xs">
                    {/* Circle marker on line */}
                    <div
                      className={`absolute -left-6 top-1 w-2.5 h-2.5 rounded-full border-2 ${
                        isFailed
                          ? 'border-red-500 bg-red-950'
                          : isSuccess
                          ? 'border-emerald-400 bg-emerald-950'
                          : 'border-blue-400 bg-blue-950'
                      }`}
                    />

                    <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80 space-y-1">
                      <div className="flex flex-wrap items-center justify-between text-[11px] text-slate-400">
                        <span className="font-mono text-slate-300">{ev.timestamp}</span>
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-blue-400">{ev.source_ip}</span>
                          <span
                            className={`px-1.5 py-0.2 rounded font-mono text-[10px] uppercase font-semibold ${
                              isFailed
                                ? 'bg-red-950/60 text-red-400 border border-red-900/40'
                                : 'bg-emerald-950/60 text-emerald-400 border border-emerald-900/40'
                            }`}
                          >
                            {ev.status}
                          </span>
                        </div>
                      </div>
                      <div className="text-slate-300 font-medium font-mono text-[11px]">
                        Target: <span className="text-blue-300">{ev.username}</span> ({ev.event_type})
                      </div>
                      <div className="text-slate-500 font-mono text-[10px] truncate">
                        {ev.raw_message}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Col: Hindsight Memory & Feedback Form */}
        <div className="space-y-6">
          {/* Hindsight Persistent Memory Box */}
          <div className="p-5 rounded-xl bg-purple-950/20 border border-purple-900/40 space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-xs font-semibold text-purple-300 uppercase tracking-wider flex items-center gap-1.5">
                <Brain className="w-4 h-4 text-purple-400" />
                Hindsight Persistent Memory
              </h2>
              <span className="text-[10px] text-purple-400 font-mono">Bank: threatlens-security-memory</span>
            </div>

            <div className="p-3 rounded-lg bg-slate-950/80 border border-purple-900/30 text-xs">
              <span className="text-slate-500 block mb-1 font-semibold">Memory Recall Intelligence:</span>
              <p className="text-slate-300 leading-relaxed">
                {incident.memory_explanation || 'No relevant historical memory found.'}
              </p>
            </div>

            {incident.retrieved_memories && incident.retrieved_memories.length > 0 && (
              <div className="space-y-2">
                <span className="text-[11px] font-semibold text-purple-400">
                  Retrieved Historical Memories ({incident.retrieved_memories.length}):
                </span>
                {incident.retrieved_memories.map((mem, mIdx) => (
                  <div
                    key={mIdx}
                    className="p-2.5 rounded bg-slate-950/90 border border-purple-900/40 text-[11px] text-slate-300 font-mono"
                  >
                    <div className="text-[10px] text-purple-400 font-semibold mb-1">
                      Reference #{mIdx + 1} • {mem.document_id || 'incident-record'}
                    </div>
                    {mem.text}
                  </div>
                ))}
              </div>
            )}

            {incident.memory_synthesis && (
              <div className="p-3 rounded-lg bg-purple-950/40 border border-purple-800/60 text-xs space-y-1">
                <span className="text-purple-300 font-semibold flex items-center gap-1">
                  <Sparkles className="w-3 h-3 text-purple-400" /> Hindsight Reflection Synthesis:
                </span>
                <p className="text-slate-300 text-[11px] leading-relaxed">
                  {incident.memory_synthesis}
                </p>
              </div>
            )}
          </div>

          {/* Defensive Recommendations */}
          <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <Cpu className="w-4 h-4 text-blue-400" />
                Defensive Recommendations
              </h2>
              <span className="text-[10px] text-amber-400 font-mono bg-amber-950/40 px-2 py-0.5 rounded border border-amber-900/40">
                Human Approval Required
              </span>
            </div>

            <div className="space-y-3">
              {(incident.recommendations || []).map((rec, rIdx) => {
                const isAccepted = acceptedRecs[rec.action] ?? true;

                return (
                  <div
                    key={rec.id || rIdx}
                    onClick={() => toggleRec(rec.action)}
                    className={`p-3 rounded-lg border cursor-pointer transition text-xs space-y-1.5 ${
                      isAccepted
                        ? 'bg-blue-950/30 border-blue-800/80 shadow-[0_0_10px_rgba(59,130,246,0.1)]'
                        : 'bg-slate-950/50 border-slate-800 opacity-60'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={isAccepted}
                          onChange={() => {}}
                          className="rounded border-slate-700 bg-slate-900 text-blue-500 focus:ring-0"
                        />
                        <span className="font-semibold text-slate-200">
                          {rec.action}
                        </span>
                      </div>
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-800">
                        {rec.priority || 'High'}
                      </span>
                    </div>

                    <p className="text-slate-400 text-[11px] pl-6">
                      {rec.description}
                    </p>

                    <div className="pl-6 pt-1 text-[10px] text-slate-500 italic">
                      Rationale: {rec.rationale}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Analyst Feedback & Learning Agent Form */}
          <form
            onSubmit={handleFeedbackSubmit}
            className="p-5 rounded-xl bg-slate-900/80 border border-emerald-900/40 space-y-4"
          >
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <h2 className="text-xs font-semibold text-emerald-300 uppercase tracking-wider flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                Analyst Confirmation & Retain
              </h2>
              <span className="text-[10px] text-emerald-400 font-mono">Agent 5: Learning</span>
            </div>

            {feedbackStatus && (
              <div
                className={`p-3 rounded-lg text-xs flex items-start gap-2 ${
                  feedbackStatus.type === 'success'
                    ? 'bg-emerald-950/60 border border-emerald-800/80 text-emerald-300'
                    : 'bg-red-950/60 border border-red-800/80 text-red-300'
                }`}
              >
                {feedbackStatus.type === 'success' ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                ) : (
                  <XCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
                )}
                <div>
                  <div className="font-semibold">{feedbackStatus.message}</div>
                  {feedbackStatus.retentionStatus && (
                    <div className="text-[10px] mt-1 font-mono text-slate-300">
                      Hindsight Retain Status: <span className="uppercase font-bold">{feedbackStatus.retentionStatus}</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Confirm Finding Toggle */}
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="findingConfirmed"
                checked={findingConfirmed}
                onChange={(e) => setFindingConfirmed(e.target.checked)}
                className="rounded border-slate-700 bg-slate-900 text-emerald-500 focus:ring-0"
              />
              <label htmlFor="findingConfirmed" className="text-xs font-medium text-slate-200 cursor-pointer">
                Confirm as Valid Security Incident (Not False Positive)
              </label>
            </div>

            {/* Confirmed Root Cause */}
            <div>
              <label className="block text-[11px] font-semibold text-slate-400 uppercase mb-1">
                Confirmed Root Cause
              </label>
              <input
                type="text"
                value={confirmedRootCause}
                onChange={(e) => setConfirmedRootCause(e.target.value)}
                required
                className="w-full px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
                placeholder="e.g. Credential stuffing using compromised credentials from public dump"
              />
            </div>

            {/* Resolution Notes */}
            <div>
              <label className="block text-[11px] font-semibold text-slate-400 uppercase mb-1">
                Resolution & Containment Notes
              </label>
              <textarea
                rows={3}
                value={resolutionNotes}
                onChange={(e) => setResolutionNotes(e.target.value)}
                required
                className="w-full p-2.5 rounded-lg bg-slate-950 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
                placeholder="Detail tactical actions applied: firewall rules, token revoking, policy hardening..."
              />
            </div>

            <button
              type="submit"
              disabled={submittingFeedback}
              className="w-full py-2.5 px-4 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs flex items-center justify-center gap-2 transition shadow-[0_0_15px_rgba(16,185,129,0.3)] disabled:opacity-50"
            >
              {submittingFeedback ? (
                <>
                  <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Retaining to Hindsight...
                </>
              ) : (
                <>
                  <Send className="w-3.5 h-3.5" />
                  Confirm & Retain in Hindsight
                </>
              )}
            </button>
            <p className="text-[10px] text-slate-500 text-center">
              Learning Agent will store this confirmed incident in <code className="text-purple-400 font-mono">threatlens-security-memory</code> for future recall.
            </p>
          </form>
        </div>
      </div>
    </div>
  );
}
