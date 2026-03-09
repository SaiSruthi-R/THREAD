import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { LayoutDashboard, FolderKanban, Search, Network, Clock, Sparkles } from 'lucide-react';
import Dashboard from './components/Dashboard';
import ProjectsView from './components/ProjectsView';
import AskMemory from './components/AskMemory';
import KnowledgeGraph from './components/KnowledgeGraph';
import DecisionTimeline from './components/DecisionTimeline';
import AIAssistant from './components/AIAssistant';
import './index.css';

function App() {
  return (
    <Router>
      <div className="flex min-h-screen bg-navy-900">
        {/* Sidebar */}
        <aside className="w-64 bg-navy-800 border-r border-navy-700 p-6">
          <div className="mb-8">
            <h1 className="text-2xl font-mono font-bold text-lime-400">Memory Map</h1>
            <p className="text-xs text-gray-500 mt-1">Contextual Knowledge System</p>
          </div>
          
          <nav className="space-y-2">
            <NavLink to="/" icon={<LayoutDashboard />} label="Dashboard" />
            <NavLink to="/projects" icon={<FolderKanban />} label="Projects" />
            <NavLink to="/ask" icon={<Search />} label="Ask Memory" />
            <NavLink to="/graph" icon={<Network />} label="Knowledge Graph" />
            <NavLink to="/timeline" icon={<Clock />} label="Decision Timeline" />
            <NavLink to="/ai-assistant" icon={<Sparkles />} label="AI Assistant" />
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/projects" element={<ProjectsView />} />
            <Route path="/ask" element={<AskMemory />} />
            <Route path="/graph" element={<KnowledgeGraph />} />
            <Route path="/timeline" element={<DecisionTimeline />} />
            <Route path="/ai-assistant" element={<AIAssistant />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

const NavLink = ({ to, icon, label }) => (
  <Link
    to={to}
    className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-400 hover:bg-navy-700 hover:text-lime-400 transition"
  >
    {icon}
    <span className="font-medium">{label}</span>
  </Link>
);

export default App;
