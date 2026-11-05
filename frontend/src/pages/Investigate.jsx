import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Upload,
  FileText,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  Sparkles,
  Database,
  ShieldAlert,
  Cpu,
  Crosshair,
  Brain,
  Code2,
  Clock,
  Layers,
  Check,
  XCircle,
  FileCheck
} from 'lucide-react';
import { uploadLogs, investigateThreat } from '../api/client';
import SeverityBadge from '../components/SeverityBadge';

const SAMPLE_INCIDENT_1 = [
  {
    "timestamp": "2026-11-05T08:14:02Z",
    "source_ip": "198.51.100.42",
    "destination_ip": "10.0.4.15",
    "username": "admin_sarah",
    "event_type": "ssh_login",
    "status": "failed",
    "raw_message": "sshd[4102]: Failed password for invalid user admin_sarah from 198.51.100.42 port 48122 ssh2"
  },
  {
    "timestamp": "2026-11-05T08:14:08Z",
    "source_ip": "198.51.100.42",
    "destination_ip": "10.0.4.15",
    "username": "admin_sarah",
    "event_type": "ssh_login",
    "status": "failed",
    "raw_message": "sshd[4105]: Failed password for admin_sarah from 198.51.100.42 port 48130 ssh2"
  },
  {
    "timestamp": "2026-11-05T08:14:15Z",
    "source_ip": "198.51.100.42",
    "destination_ip": "10.0.4.15",
    "username": "admin_sarah",
    "event_type": "ssh_login",
    "status": "failed",
    "raw_message": "sshd[4110]: Failed password for admin_sarah from 198.51.100.42 port 48144 ssh2"
  },
  {
    "timestamp": "2026-11-05T08:14:22Z",
    "source_ip": "198.51.100.42",
    "destination_ip": "10.0.4.15",
    "username": "secops_lead",
    "event_type": "web_portal_auth",
    "status": "failed",
    "raw_message": "auth-service[1092]: Invalid credential hash for secops_lead from 198.51.100.42"
  },
  {
    "timestamp": "2026-11-05T08:14:30Z",
    "source_ip": "198.51.100.42",
    "destination_ip": "10.0.4.15",
    "username": "secops_lead",
    "event_type": "web_portal_auth",
    "status": "failed",
    "raw_message": "auth-service[1098]: Authentication failure for secops_lead from 198.51.100.42 attempt 2"
  },
  {
    "timestamp": "2026-11-05T08:14:48Z",
    "source_ip": "198.51.100.42",
    "destination_ip": "10.0.4.15",
    "username": "dev_alex",
    "event_type": "vpn_auth",
    "status": "failed",
    "raw_message": "openvpn[882]: Bad credentials for user dev_alex from 198.51.100.42"
  },
  {
    "timestamp": "2026-11-05T08:15:10Z",
    "source_ip": "198.51.100.42",
    "destination_ip": "10.0.4.15",
    "username": "admin_sarah",
    "event_type": "ssh_login",
    "status": "success",
    "raw_message": "sshd[4150]: Accepted password for admin_sarah from 198.51.100.42 port 48190 ssh2 [BREAKTHROUGH POST-FAILURE]"
  },
  {
    "timestamp": "2026-11-05T08:15:25Z",
    "source_ip": "198.51.100.42",
    "destination_ip": "10.0.4.15",
    "username": "admin_sarah",
    "event_type": "privilege_command",
    "status": "success",
    "raw_message": "sudo: admin_sarah : TTY=pts/2 ; USER=root ; COMMAND=/bin/cat /etc/shadow"
  }
];

const SAMPLE_INCIDENT_2 = [
  {
    "timestamp": "2026-11-05T09:30:11Z",
    "source_ip": "198.51.100.89",
    "destination_ip": "10.0.4.20",
    "username": "admin_jordan",
    "event_type": "ssh_login",
    "status": "failed",
    "raw_message": "sshd[5201]: Failed password for invalid user admin_jordan from 198.51.100.89 port 51100 ssh2"
  },
  {
    "timestamp": "2026-11-05T09:30:18Z",
    "source_ip": "198.51.100.89",
    "destination_ip": "10.0.4.20",
    "username": "admin_jordan",
    "event_type": "ssh_login",
    "status": "failed",
    "raw_message": "sshd[5204]: Failed password for admin_jordan from 198.51.100.89 port 51108 ssh2"
  },
  {
    "timestamp": "2026-11-05T09:30:25Z",
    "source_ip": "198.51.100.89",
    "destination_ip": "10.0.4.20",
    "username": "admin_jordan",
    "event_type": "ssh_login",
    "status": "failed",
    "raw_message": "sshd[5210]: Failed password for admin_jordan from 198.51.100.89 port 51114 ssh2"
  },
  {
    "timestamp": "2026-11-05T09:30:33Z",
    "source_ip": "198.51.100.89",
    "destination_ip": "10.0.4.20",
    "username": "finance_ops",
    "event_type": "web_portal_auth",
    "status": "failed",
    "raw_message": "auth-service[2100]: Invalid password hash for finance_ops from 198.51.100.89"
  },
  {
    "timestamp": "2026-11-05T09:30:41Z",
    "source_ip": "198.51.100.89",
    "destination_ip": "10.0.4.20",
    "username": "finance_ops",
    "event_type": "web_portal_auth",
    "status": "failed",
    "raw_message": "auth-service[2105]: Authentication failure attempt 2 for finance_ops from 198.51.100.89"
  },
  {
    "timestamp": "2026-11-05T09:31:05Z",
    "source_ip": "198.51.100.89",
    "destination_ip": "10.0.4.20",
    "username": "admin_jordan",
    "event_type": "ssh_login",
    "status": "success",
    "raw_message": "sshd[5240]: Accepted password for admin_jordan from 198.51.100.89 port 51160 ssh2 [SIMILAR SPRAY BREAKTHROUGH]"
  }
];

const SAMPLE_BASELINE = [
  {
    "timestamp": "2026-11-05T08:00:10Z",
    "source_ip": "10.0.1.50",
    "destination_ip": "10.0.4.15",
    "username": "alice_dev",
    "event_type": "sso_login",
    "status": "success",
    "raw_message": "sso-idp[801]: User alice_dev successfully authenticated via SAML 2.0 with MFA push"
  },
  {
    "timestamp": "2026-11-05T08:02:15Z",
    "source_ip": "10.0.1.55",
    "destination_ip": "10.0.4.15",
    "username": "bob_qa",
    "event_type": "vpn_auth",
    "status": "success",
    "raw_message": "openvpn[805]: TLS handshake succeeded; user bob_qa authenticated from corp-wifi"
  },
  {
    "timestamp": "2026-11-05T08:05:22Z",
    "source_ip": "10.0.1.60",
    "destination_ip": "10.0.4.20",
    "username": "carol_eng",
    "event_type": "web_portal_auth",
    "status": "success",
    "raw_message": "auth-service[812]: Valid session ticket issued for carol_eng"
  },
  {
    "timestamp": "2026-11-05T08:10:00Z",
    "source_ip": "10.0.1.62",
    "destination_ip": "10.0.4.20",
    "username": "dave_ops",
    "event_type": "ssh_login",
    "status": "success",
    "raw_message": "sshd[820]: Accepted publickey for dave_ops from 10.0.1.62 port 42100 ssh2"
  },
  {
    "timestamp": "2026-11-05T08:15:30Z",
    "source_ip": "10.0.1.50",
    "destination_ip": "10.0.4.15",
    "username": "alice_dev",
    "event_type": "api_request",
    "status": "success",
    "raw_message": "api-gateway[830]: GET /api/v1/projects 200 OK for user alice_dev"
  },
  {
    "timestamp": "2026-11-05T08:20:45Z",
    "source_ip": "10.0.1.70",
    "destination_ip": "10.0.4.20",
    "username": "emma_hr",
    "event_type": "sso_login",
    "status": "success",
    "raw_message": "sso-idp[845]: Routine SSO login for emma_hr from workstation WKSTN-08"
  }
];

const INITIAL_AGENT_STEPS = [
  { id: 'detection', name: 'Threat Detection Agent', role: 'Rule execution & log pattern analysis', status: 'pending' },
  { id: 'investigation', name: 'Investigation Agent', role: 'Timeline creation & hypothesis testing', status: 'pending' },
  { id: 'memory', name: 'Hindsight Memory Agent', role: 'Recall & reflect across memory bank', status: 'pending' },
  { id: 'response', name: 'Response Agent', role: 'Defensive recommendations formulation', status: 'pending' },
  { id: 'learning', name: 'Learning Agent', role: 'Retains verified knowledge post-analyst review', status: 'pending' },
];

function formatBytes(bytes) {
  if (bytes === 0 || !bytes) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

export default function Investigate() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [fileUploadMeta, setFileUploadMeta] = useState(null);
  const [logText, setLogText] = useState(JSON.stringify(SAMPLE_INCIDENT_1, null, 2));
  const [activeSample, setActiveSample] = useState(1);
  const [customTitle, setCustomTitle] = useState('Incident 1: Initial Credential Attack');
  const [isProcessing, setIsProcessing] = useState(false);
  const [agentSteps, setAgentSteps] = useState(INITIAL_AGENT_STEPS);
  const [errorMsg, setErrorMsg] = useState(null);
  const [result, setResult] = useState(null);

  const loadSample = (sampleNum) => {
    setActiveSample(sampleNum);
    setFile(null);
    setFileUploadMeta(null);
    setResult(null);
    setErrorMsg(null);
    setAgentSteps(INITIAL_AGENT_STEPS);

    if (sampleNum === 1) {
      setLogText(JSON.stringify(SAMPLE_INCIDENT_1, null, 2));
      setCustomTitle('Incident 1: Credential Attack & Compromise');
    } else if (sampleNum === 2) {
      setLogText(JSON.stringify(SAMPLE_INCIDENT_2, null, 2));
      setCustomTitle('Incident 2: Similar Credential Attack (Hindsight Memory Test)');
    } else {
      setLogText(JSON.stringify(SAMPLE_BASELINE, null, 2));
      setCustomTitle('Baseline Audit: Normal Authentication Baseline');
    }
  };

  const handleFileUpload = async (e) => {
    const uploadedFile = e.target.files[0];
    if (!uploadedFile) return;

    // Strict 100 MB client check (104857600 bytes)
    if (uploadedFile.size > 104857600) {
      setErrorMsg(`File exceeds maximum allowed size of 100 MB (104857600 bytes). Selected size: ${formatBytes(uploadedFile.size)}`);
      setFile(null);
      setFileUploadMeta(null);
      return;
    }

    setFile(uploadedFile);
    setActiveSample(null);
    setResult(null);
    setErrorMsg(null);
    setCustomTitle(`Investigation: ${uploadedFile.name.replace(/\.[^/.]+$/, '')}`);
    setAgentSteps(INITIAL_AGENT_STEPS);

    const formData = new FormData();
    formData.append('file', uploadedFile);

    try {
      const uploadRes = await uploadLogs(formData);
      setLogText(JSON.stringify(uploadRes.events, null, 2));
      setFileUploadMeta({
        name: uploadedFile.name,
        size: uploadedFile.size,
        eventCount: uploadRes.event_count,
        rejectedCount: uploadRes.rejected_count,
        format: uploadRes.format,
        errors: uploadRes.parsing_errors || []
      });
      setErrorMsg(null);
    } catch (err) {
      const detail = err.response?.data?.detail || 'Failed to parse log file.';
      setErrorMsg(detail);
      setFileUploadMeta(null);
    }
  };

  const handleStartInvestigation = async () => {
    setIsProcessing(true);
    setErrorMsg(null);
    setResult(null);

    let parsedEvents = [];
    try {
      parsedEvents = JSON.parse(logText);
      if (!Array.isArray(parsedEvents)) {
        throw new Error('Payload must be a JSON array of event objects.');
      }
      if (parsedEvents.length === 0) {
        throw new Error('No security events found in the payload.');
      }
    } catch (e) {
      setErrorMsg(`Invalid log payload: ${e.message}`);
      setIsProcessing(false);
      return;
    }

    // Set agents to running progression
    setAgentSteps([
      { id: 'detection', name: 'Threat Detection Agent', role: 'Rule execution & log pattern analysis', status: 'running' },
      { id: 'investigation', name: 'Investigation Agent', role: 'Timeline creation & hypothesis testing', status: 'pending' },
      { id: 'memory', name: 'Hindsight Memory Agent', role: 'Recall & reflect across memory bank', status: 'pending' },
      { id: 'response', name: 'Response Agent', role: 'Defensive recommendations formulation', status: 'pending' },
      { id: 'learning', name: 'Learning Agent', role: 'Retains verified knowledge post-analyst review', status: 'pending' },
    ]);

    try {
      const response = await investigateThreat({
        events: parsedEvents,
        title: customTitle,
      });

      const data = response.data;
      setResult(data);

      // Apply real backend agent statuses
      if (data.agent_execution) {
        setAgentSteps([
          { id: 'detection', name: 'Threat Detection Agent', role: 'Rule execution & log pattern analysis', status: data.agent_execution.detection?.status || 'completed' },
          { id: 'investigation', name: 'Investigation Agent', role: 'Timeline creation & hypothesis testing', status: data.agent_execution.investigation?.status || 'completed' },
          { id: 'memory', name: 'Hindsight Memory Agent', role: 'Recall & reflect across memory bank', status: data.agent_execution.memory?.status || 'completed' },
          { id: 'response', name: 'Response Agent', role: 'Defensive recommendations formulation', status: data.agent_execution.response?.status || 'completed' },
          { id: 'learning', name: 'Learning Agent', role: 'Retains verified knowledge post-analyst review', status: 'pending_confirmation' },
        ]);
      } else {
        setAgentSteps((prev) => prev.map((s) => ({ ...s, status: 'completed' })));
      }
    } catch (err) {
      const msg = err.response?.data?.detail || 'Investigation pipeline failed.';
      setErrorMsg(msg);
      setAgentSteps((prev) => prev.map((s) => ({ ...s, status: s.status === 'running' ? 'failed' : s.status })));
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-100 tracking-tight flex items-center gap-2">
          Investigate Security Threat
          <span className="text-xs px-2 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30 font-normal">
            Multi-Agent Pipeline
          </span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Upload and normalize CSV/JSON logs, execute Threat Detection & Investigation agents, recall historical incident intelligence via Hindsight, and formulate defensive recommendations.
        </p>
      </div>

      {/* Error alert */}
      {errorMsg && (
        <div className="p-4 rounded-xl bg-red-950/70 border border-red-800 text-red-200 text-xs flex items-start gap-2.5 shadow-lg">
          <AlertCircle className="w-4 h-4 shrink-0 text-red-400 mt-0.5" />
          <div>
            <span className="font-semibold block mb-0.5">Investigation Pipeline Error</span>
            <span>{errorMsg}</span>
          </div>
        </div>
      )}

      {/* Sample Selectors & File Upload */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Sample 1: Credential Attack */}
        <button
          onClick={() => loadSample(1)}
          className={`p-3.5 rounded-xl text-left border transition relative ${
            activeSample === 1
              ? 'bg-blue-950/40 border-blue-500 shadow-[0_0_15px_rgba(59,130,246,0.2)]'
              : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
          }`}
        >
          <div className="flex items-center justify-between text-xs font-semibold text-slate-200 mb-1">
            <span className="flex items-center gap-1.5">
              <ShieldAlert className="w-4 h-4 text-red-400" />
              Incident 1: Attack
            </span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-red-900/40 text-red-300 font-mono">
              8 Events
            </span>
          </div>
          <p className="text-[11px] text-slate-400 line-clamp-2">
            Brute force spray from 198.51.100.42 culminating in unauthorized access.
          </p>
        </button>

        {/* Sample 2: Similar Spray */}
        <button
          onClick={() => loadSample(2)}
          className={`p-3.5 rounded-xl text-left border transition relative ${
            activeSample === 2
              ? 'bg-purple-950/40 border-purple-500 shadow-[0_0_15px_rgba(168,85,247,0.2)]'
              : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
          }`}
        >
          <div className="flex items-center justify-between text-xs font-semibold text-slate-200 mb-1">
            <span className="flex items-center gap-1.5">
              <Brain className="w-4 h-4 text-purple-400" />
              Incident 2: Sibling Attack
            </span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-purple-900/40 text-purple-300 font-mono">
              6 Events
            </span>
          </div>
          <p className="text-[11px] text-slate-400 line-clamp-2">
            Similar spray from 198.51.100.89. Verifies Hindsight persistent recall!
          </p>
        </button>

        {/* Sample 3: Normal Baseline */}
        <button
          onClick={() => loadSample(3)}
          className={`p-3.5 rounded-xl text-left border transition relative ${
            activeSample === 3
              ? 'bg-emerald-950/40 border-emerald-500 shadow-[0_0_15px_rgba(16,185,129,0.2)]'
              : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
          }`}
        >
          <div className="flex items-center justify-between text-xs font-semibold text-slate-200 mb-1">
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              Normal Baseline
            </span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-900/40 text-emerald-300 font-mono">
              6 Events
            </span>
          </div>
          <p className="text-[11px] text-slate-400 line-clamp-2">
            Authorized corporate SSO/VPN baseline. Verifies zero false positive classification.
          </p>
        </button>

        {/* File Upload Area */}
        <label className="p-3.5 rounded-xl border border-dashed border-slate-700 bg-slate-900/40 hover:bg-slate-900/80 cursor-pointer flex flex-col items-center justify-center text-center transition">
          <Upload className="w-5 h-5 text-blue-400 mb-1" />
          <span className="text-xs font-semibold text-slate-200">
            {file ? file.name : 'Upload CSV / JSON Log'}
          </span>
          <span className="text-[10px] text-slate-500 mt-0.5">
            Max 100 MB • Auto-validated schema
          </span>
          <input
            type="file"
            accept=".csv,.json"
            onChange={handleFileUpload}
            className="hidden"
          />
        </label>
      </div>

      {/* Uploaded File Metadata Banner */}
      {fileUploadMeta && (
        <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-700/80 flex flex-wrap items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-2">
            <FileCheck className="w-4 h-4 text-emerald-400 shrink-0" />
            <span className="text-slate-200 font-medium">{fileUploadMeta.name}</span>
            <span className="text-slate-500">({formatBytes(fileUploadMeta.size)})</span>
            <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[11px] font-mono uppercase">
              {fileUploadMeta.format}
            </span>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-emerald-400 font-semibold flex items-center gap-1">
              <Check className="w-3.5 h-3.5" />
              {fileUploadMeta.eventCount} valid events parsed
            </span>
            {fileUploadMeta.rejectedCount > 0 && (
              <span className="text-amber-400 font-mono text-[11px]">
                ({fileUploadMeta.rejectedCount} invalid rows rejected)
              </span>
            )}
          </div>
        </div>
      )}

      {/* Investigation Details & Log Input Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Title & Raw Log Preview */}
        <div className="lg:col-span-2 space-y-4">
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              Investigation Title
            </label>
            <input
              type="text"
              value={customTitle}
              onChange={(e) => setCustomTitle(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-700 text-xs text-slate-200 font-medium focus:outline-none focus:border-blue-500"
              placeholder="e.g. Investigation: Credential Stuffing & Brute Force Campaign"
            />
          </div>

          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <Code2 className="w-4 h-4 text-blue-400" />
                Security Log Payload (Normalized JSON)
              </span>
              <span className="text-[11px] text-slate-500 font-mono">
                Untrusted Input Sanitized • Real Values Preserved
              </span>
            </div>
            <textarea
              rows={11}
              value={logText}
              onChange={(e) => setLogText(e.target.value)}
              className="w-full p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-300 font-mono focus:outline-none focus:border-blue-500 resize-y"
            />
          </div>
        </div>

        {/* Right Col: Execution Control & Agent Progress */}
        <div className="space-y-4">
          {/* Action Card */}
          <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800">
            <h3 className="text-sm font-semibold text-slate-200 mb-1">
              Multi-Agent Orchestration
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Executes Detection, Investigation, Hindsight Memory, and Response Recommendation agents across the security logs.
            </p>

            <button
              onClick={handleStartInvestigation}
              disabled={isProcessing}
              className={`w-full py-3 px-4 rounded-lg font-semibold text-xs flex items-center justify-center gap-2 transition shadow-lg ${
                isProcessing
                  ? 'bg-blue-800 text-blue-200 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-500 text-white shadow-[0_0_20px_rgba(59,130,246,0.35)]'
              }`}
            >
              {isProcessing ? (
                <>
                  <Sparkles className="w-4 h-4 animate-spin" />
                  Agents Investigating Pipeline...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Start Multi-Agent Investigation
                </>
              )}
            </button>
          </div>

          {/* Agent Pipeline Visualizer */}
          <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800">
            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
              Agent Execution Mesh
            </h4>
            <div className="space-y-2.5">
              {agentSteps.map((step) => {
                const isRunning = step.status === 'running';
                const isDone = step.status === 'completed';
                const isFailed = step.status === 'failed';
                const isPendingReview = step.status === 'pending_analyst_review' || step.status === 'pending_confirmation';

                return (
                  <div
                    key={step.id}
                    className={`p-2.5 rounded-lg border transition ${
                      isRunning
                        ? 'bg-blue-950/40 border-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.2)]'
                        : isDone
                        ? 'bg-slate-950/70 border-emerald-900/50'
                        : isFailed
                        ? 'bg-red-950/40 border-red-800/60'
                        : isPendingReview
                        ? 'bg-purple-950/30 border-purple-800/40'
                        : 'bg-slate-950/40 border-slate-800/80 opacity-60'
                    }`}
                  >
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-semibold text-slate-200 flex items-center gap-2">
                        {isDone ? (
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                        ) : isRunning ? (
                          <span className="w-3.5 h-3.5 rounded-full border-2 border-blue-400 border-t-transparent animate-spin inline-block" />
                        ) : isFailed ? (
                          <XCircle className="w-3.5 h-3.5 text-red-400" />
                        ) : isPendingReview ? (
                          <Clock className="w-3.5 h-3.5 text-purple-400" />
                        ) : (
                          <span className="w-3.5 h-3.5 rounded-full border border-slate-600 inline-block text-[9px] text-center leading-3">
                            •
                          </span>
                        )}
                        {step.name}
                      </span>
                      <span className="text-[10px] font-mono uppercase font-semibold">
                        {isDone ? (
                          <span className="text-emerald-400">COMPLETED</span>
                        ) : isRunning ? (
                          <span className="text-blue-400 animate-pulse">RUNNING</span>
                        ) : isFailed ? (
                          <span className="text-red-400">FAILED</span>
                        ) : isPendingReview ? (
                          <span className="text-purple-400">POST-REVIEW</span>
                        ) : (
                          <span className="text-slate-500">PENDING</span>
                        )}
                      </span>
                    </div>
                    <p className="text-[10px] text-slate-400 mt-1 pl-5">
                      {step.role}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Immediate Investigation Results Preview Card */}
      {result && (
        <div className="p-6 rounded-xl bg-slate-900/90 border border-blue-500/40 shadow-[0_0_30px_rgba(59,130,246,0.15)] space-y-5">
          {/* Top row: ID, Severity, Title, Action Button */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
            <div>
              <div className="flex flex-wrap items-center gap-2 mb-1">
                <span className="text-xs font-mono text-blue-400 font-semibold">
                  {result.incident.incident_id}
                </span>
                <SeverityBadge severity={result.incident.severity} />

                {/* Hindsight Status Badge */}
                {result.memory?.hindsight_status === 'recalled' ? (
                  <span className="px-2 py-0.5 rounded text-xs bg-purple-950/70 text-purple-300 border border-purple-800 flex items-center gap-1 font-medium">
                    <Brain className="w-3 h-3 text-purple-400" />
                    Hindsight Memory Recalled ({result.memory.memory_count})
                  </span>
                ) : result.memory?.hindsight_status === 'unavailable' ? (
                  <span className="px-2 py-0.5 rounded text-xs bg-amber-950/70 text-amber-300 border border-amber-800 flex items-center gap-1 font-medium">
                    <AlertCircle className="w-3 h-3 text-amber-400" />
                    Memory Unavailable (Non-Memory Analysis)
                  </span>
                ) : (
                  <span className="px-2 py-0.5 rounded text-xs bg-slate-800/80 text-slate-400 border border-slate-700 flex items-center gap-1 font-medium">
                    No Matching Historical Memory
                  </span>
                )}

                <span className="text-[11px] text-slate-500 font-mono ml-auto">
                  {new Date(result.incident.created_at || Date.now()).toUTCString()}
                </span>
              </div>

              <h2 className="text-lg font-bold text-slate-100">
                {result.incident.title}
              </h2>
            </div>

            <button
              onClick={() => navigate(`/incidents/${result.incident.incident_id}`)}
              className="px-4 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center gap-2 transition shrink-0 shadow-[0_0_15px_rgba(59,130,246,0.3)]"
            >
              Inspect Complete Incident Details <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {/* Quick Stats Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800">
              <span className="text-slate-500 block mb-1">Attack Classification</span>
              <span className="text-slate-200 font-semibold">{result.detection.attack_type}</span>
            </div>
            <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800">
              <span className="text-slate-500 block mb-1">Analyzed / Suspicious Events</span>
              <span className="text-slate-200 font-mono font-semibold">
                {result.incident.analyzed_events_count || result.incident.event_count || 0} / {result.incident.suspicious_events_count || 0}
              </span>
            </div>
            <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800">
              <span className="text-slate-500 block mb-1">Source IP Addresses</span>
              <span className="text-slate-200 font-mono">
                {result.incident.source_ips?.length > 0
                  ? result.incident.source_ips.join(', ')
                  : 'None (Internal / Baseline)'}
              </span>
            </div>
            <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800">
              <span className="text-slate-500 block mb-1">Targeted Usernames</span>
              <span className="text-slate-200 font-mono">
                {result.incident.targeted_users?.length > 0
                  ? result.incident.targeted_users.join(', ')
                  : 'None (Baseline)'}
              </span>
            </div>
          </div>

          {/* Investigation Narrative & Evidence */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            {/* Narrative */}
            <div className="p-4 rounded-lg bg-slate-950/80 border border-slate-800 space-y-2">
              <span className="font-semibold text-slate-200 block uppercase tracking-wider text-[11px]">
                Investigation Narrative & Pattern
              </span>
              <p className="text-slate-300 leading-relaxed">
                {result.investigation.summary}
              </p>
              <div className="pt-2 text-[11px] text-slate-400">
                <span className="text-slate-500 font-semibold">Attack Pattern: </span>
                <span className="font-mono text-blue-300">{result.investigation.attack_pattern || 'N/A'}</span>
              </div>
            </div>

            {/* Evidence & Observed Facts */}
            <div className="p-4 rounded-lg bg-slate-950/80 border border-slate-800 space-y-2">
              <span className="font-semibold text-slate-200 block uppercase tracking-wider text-[11px]">
                Observed Facts & Telemetry Evidence
              </span>
              <ul className="space-y-1.5 text-slate-300">
                {(result.investigation.observed_facts || []).slice(0, 4).map((fact, idx) => (
                  <li key={idx} className="flex items-start gap-1.5">
                    <span className="text-blue-400 font-bold">•</span>
                    <span>{fact}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Recalled Hindsight Historical Intelligence (if memories exist) */}
          {result.memory?.retrieved_memories?.length > 0 && (
            <div className="p-4 rounded-lg bg-purple-950/20 border border-purple-800/40 space-y-2 text-xs">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-purple-300 uppercase tracking-wider text-[11px] flex items-center gap-1.5">
                  <Brain className="w-3.5 h-3.5 text-purple-400" />
                  Recalled Historical Incident Intelligence ({result.memory.retrieved_memories.length} items)
                </span>
                <span className="text-[10px] text-purple-400 font-mono">
                  Bank: {result.memory.bank_id}
                </span>
              </div>
              <div className="space-y-1.5">
                {result.memory.retrieved_memories.slice(0, 2).map((m, idx) => (
                  <div key={idx} className="p-2.5 rounded bg-slate-950/60 border border-purple-900/40 text-slate-300 text-[11px]">
                    <div className="flex items-center gap-2 mb-1 text-[10px] text-purple-400 font-mono">
                      <span>Memory ID: {m.id?.slice(0, 8)}...</span>
                      {m.scores?.final && (
                        <span>Relevance: {(m.scores.final * 100).toFixed(0)}%</span>
                      )}
                    </div>
                    <p className="line-clamp-2">{m.text}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommended Defensive Actions Preview */}
          {result.response?.recommended_actions?.length > 0 && (
            <div className="p-4 rounded-lg bg-slate-950/80 border border-slate-800 space-y-2.5 text-xs">
              <span className="font-semibold text-slate-200 block uppercase tracking-wider text-[11px]">
                Recommended Defensive Actions ({result.response.recommended_actions.length} prioritized)
              </span>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                {result.response.recommended_actions.slice(0, 4).map((rec, idx) => (
                  <div key={idx} className="p-2.5 rounded bg-slate-900/60 border border-slate-800 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-200">{rec.action}</span>
                      <span className={`text-[10px] px-1.5 py-0.5 rounded font-semibold ${
                        rec.priority === 'Critical' ? 'bg-red-950 text-red-400 border border-red-800' :
                        rec.priority === 'High' ? 'bg-orange-950 text-orange-400 border border-orange-800' :
                        'bg-blue-950 text-blue-400 border border-blue-800'
                      }`}>
                        {rec.priority}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400 line-clamp-2">{rec.description}</p>
                    <div className="flex items-center justify-between pt-1 text-[10px] text-slate-500">
                      <span>{rec.category}</span>
                      <span className="text-amber-400 font-medium">Requires Human Approval</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
