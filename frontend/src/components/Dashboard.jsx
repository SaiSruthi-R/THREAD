import React, { useState, useEffect } from 'react';
import { Activity, Users, FolderKanban, Brain } from 'lucide-react';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_BASE || 'https://api.example.com';

const Dashboard = () => {
  const [stats, setStats] = useState({
    projectsCount: 0,
    decisionsCount: 0,
    knowledgeItems: 0,
    teamMembers: 0
  });
  const [projects, setProjects] = useState([]);
  const [activities, setActivities] = useState([]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [projectsRes, decisionsRes] = await Promise.all([
        axios.get(`${API_BASE}/projects`),
        axios.get(`${API_BASE}/decisions`)
      ]);
      
      const projectsData = projectsRes.data.projects || [];
      const decisionsData = decisionsRes.data.decisions || [];
      
      setProjects(projectsData.slice(0, 3));
      setStats({
        projectsCount: projectsData.filter(p => p.status === 'active').length,
        decisionsCount: decisionsData.length,
        knowledgeItems: projectsData.reduce((sum, p) => sum + (p.knowledgeItemCount || 0), 0),
        teamMembers: new Set(projectsData.flatMap(p => p.members || [])).size
      });
      
      setActivities(decisionsData.slice(0, 5).map(d => ({
        text: d.title || d.description,
        timestamp: d.timestamp
      })));
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    }
  };

  const timelineSteps = [
    { label: 'Kickoff', status: 'completed' },
    { label: 'Architecture Review', status: 'completed' },
    { label: 'API Dev', status: 'active' },
    { label: 'Audit', status: 'pending' },
    { label: 'Deploy', status: 'pending' }
  ];

  return (
    <div className="min-h-screen bg-navy-900 text-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-mono font-bold text-lime-400 mb-8">Memory Mapping Dashboard</h1>
        
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <StatCard icon={<FolderKanban />} label="Active Projects" value={stats.projectsCount} />
          <StatCard icon={<Brain />} label="Total Decisions" value={stats.decisionsCount} />
          <StatCard icon={<Activity />} label="Knowledge Items" value={stats.knowledgeItems} />
          <StatCard icon={<Users />} label="Team Members" value={stats.teamMembers} />
        </div>

        {/* Project Timeline */}
        <div className="bg-navy-800 rounded-lg p-6 mb-8 border border-navy-700">
          <h2 className="text-2xl font-mono font-semibold text-lime-400 mb-6">Project Timeline</h2>
          <div className="flex items-center justify-between">
            {timelineSteps.map((step, idx) => (
              <div key={idx} className="flex items-center flex-1">
                <div className="flex flex-col items-center">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center border-2 ${
                    step.status === 'completed' ? 'bg-lime-500 border-lime-500' :
                    step.status === 'active' ? 'bg-lime-400 border-lime-400 animate-pulse' :
                    'bg-navy-700 border-gray-600'
                  }`}>
                    {step.status === 'completed' && <span className="text-navy-900">✓</span>}
                  </div>
                  <span className="mt-2 text-sm text-gray-400">{step.label}</span>
                </div>
                {idx < timelineSteps.length - 1 && (
                  <div className={`flex-1 h-0.5 mx-2 ${
                    step.status === 'completed' ? 'bg-lime-500' : 'bg-gray-600'
                  }`} />
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Projects */}
          <div className="bg-navy-800 rounded-lg p-6 border border-navy-700">
            <h2 className="text-2xl font-mono font-semibold text-lime-400 mb-4">Recent Projects</h2>
            <div className="space-y-3">
              {projects.map((project, idx) => (
                <div key={idx} className="bg-navy-700 p-4 rounded border border-gray-600 hover:border-lime-400 transition">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-semibold text-gray-100">{project.name}</h3>
                    <span className={`px-2 py-1 text-xs rounded ${
                      project.status === 'active' ? 'bg-lime-500 text-navy-900' : 'bg-gray-600 text-gray-200'
                    }`}>
                      {project.status}
                    </span>
                  </div>
                  <div className="w-full bg-navy-900 rounded-full h-2 mb-2">
                    <div className="bg-lime-400 h-2 rounded-full" style={{ width: `${project.progress || 60}%` }} />
                  </div>
                  <div className="flex justify-between text-xs text-gray-400">
                    <span>{project.members?.length || 0} members</span>
                    <span>{project.decisionCount || 0} decisions</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Activities */}
          <div className="bg-navy-800 rounded-lg p-6 border border-navy-700">
            <h2 className="text-2xl font-mono font-semibold text-lime-400 mb-4">Recent Activities</h2>
            <div className="space-y-3">
              {activities.map((activity, idx) => (
                <div key={idx} className="flex items-start space-x-3 text-sm">
                  <div className="w-2 h-2 bg-lime-400 rounded-full mt-2" />
                  <div className="flex-1">
                    <p className="text-gray-300">{activity.text}</p>
                    <span className="text-xs text-gray-500">{new Date(activity.timestamp).toLocaleString()}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const StatCard = ({ icon, label, value }) => (
  <div className="bg-navy-800 rounded-lg p-6 border border-navy-700 hover:border-lime-400 transition">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-gray-400 text-sm mb-1">{label}</p>
        <p className="text-3xl font-bold text-lime-400">{value}</p>
      </div>
      <div className="text-lime-400 opacity-50">
        {icon}
      </div>
    </div>
  </div>
);

export default Dashboard;