import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import Overview from './pages/Overview';
import Investigate from './pages/Investigate';
import Incidents from './pages/Incidents';
import IncidentDetails from './pages/IncidentDetails';
import MemoryExplorer from './pages/MemoryExplorer';
import Analytics from './pages/Analytics';
import { getHealth } from './api/client';

export default function App() {
  const [healthData, setHealthData] = useState(null);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const data = await getHealth();
        setHealthData(data);
      } catch (err) {
        console.error('Failed to retrieve system health:', err);
      }
    };
    fetchHealth();
    const interval = setInterval(fetchHealth, 20000);
    return () => clearInterval(interval);
  }, []);

  return (
    <BrowserRouter>
      <div className="flex min-h-screen bg-[#0a0e17] text-slate-100 antialiased selection:bg-blue-600 selection:text-white">
        {/* Main Sidebar */}
        <Sidebar memoryStatus={healthData?.hindsight} />

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
          {/* Top SOC Navbar */}
          <Navbar healthData={healthData} />

          {/* Dynamic Page Routes */}
          <main className="flex-1 p-6 md:p-8">
            <Routes>
              <Route path="/" element={<Overview />} />
              <Route path="/investigate" element={<Investigate />} />
              <Route path="/incidents" element={<Incidents />} />
              <Route path="/incidents/:incidentId" element={<IncidentDetails />} />
              <Route path="/memory" element={<MemoryExplorer />} />
              <Route path="/analytics" element={<Analytics />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
}
