import React, { useState, useEffect } from 'react';
import { Clock, User, ExternalLink } from 'lucide-react';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_BASE || 'https://api.example.com';

const DecisionTimeline = () => {
  const [decisions, setDecisions] = useState([]);
  const [filters, setFilters] = useState({
    projectId: '',
    startDate: '',
    endDate: ''
  });

  useEffect(() => {
    fetchDecisions();
  }, [filters]);

  const fetchDecisions = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.projectId) params.append('projectId', filters.projectId);
      if (filters.startDate) params.append('startDate', filters.startDate);
      if (filters.endDate) params.append('endDate', filters.endDate);
      
      const response = await axios.get(`${API_BASE}/decisions?${params}`);
      setDecisions(response.data.decisions || []);
    } catch (error) {
      console.error('Error fetching decisions:', error);
    }
  };

  return (
    <div className="min-h-screen bg-navy-900 text-gray-100 p-6">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-4xl font-mono font-bold text-lime-400 mb-8">Decision Timeline</h1>

        {/* Filters */}
        <div className="bg-navy-800 rounded-lg p-4 mb-8 border border-navy-700">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="text-xs text-gray-400 mb-2 block">Project</label>
              <select
                value={filters.projectId}
                onChange={(e) => setFilters({ ...filters, projectId: e.target.value })}
                className="w-full bg-navy-700 border border-navy-600 rounded-lg px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-lime-400"
              >
                <option value="">All Projects</option>
                <option value="1">Platform Rebuild</option>
                <option value="2">Mobile App</option>
                <option value="3">Analytics Dashboard</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-gray-400 mb-2 block">Start Date</label>
              <input
                type="date"
                value={filters.startDate}
                onChange={(e) => setFilters({ ...filters, startDate: e.target.value })}
                className="w-full bg-navy-700 border border-navy-600 rounded-lg px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-lime-400"
              />
            </div>
            <div>
              <label className="text-xs text-gray-400 mb-2 block">End Date</label>
              <input
                type="date"
                value={filters.endDate}
                onChange={(e) => setFilters({ ...filters, endDate: e.target.value })}
                className="w-full bg-navy-700 border border-navy-600 rounded-lg px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-lime-400"
              />
            </div>
          </div>
        </div>

        {/* Timeline */}
        <div className="relative">
          {/* Vertical Line */}
          <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-navy-700" />

          {/* Decision Items */}
          <div className="space-y-8">
            {decisions.map((decision, idx) => (
              <div key={idx} className="relative pl-20">
                {/* Timeline Dot */}
                <div className="absolute left-6 top-2 w-5 h-5 bg-lime-400 rounded-full border-4 border-navy-900" />
                
                {/* Decision Card */}
                <div className="bg-navy-800 rounded-lg p-6 border border-navy-700 hover:border-lime-400 transition">
                  <div className="flex justify-between items-start mb-3">
                    <h3 className="text-xl font-semibold text-gray-100">
                      {decision.title || 'Decision'}
                    </h3>
                    <span className="text-xs text-gray-500 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {new Date(decision.timestamp).toLocaleDateString()}
                    </span>
                  </div>

                  <p className="text-gray-400 text-sm mb-4">
                    {decision.description || 'No description available'}
                  </p>

                  {/* People Involved */}
                  {decision.people && decision.people.length > 0 && (
                    <div className="flex items-center gap-2 mb-4">
                      <User className="w-4 h-4 text-gray-500" />
                      <div className="flex gap-2">
                        {decision.people.map((person, pidx) => (
                          <span
                            key={pidx}
                            className="text-xs bg-navy-700 px-2 py-1 rounded text-gray-300"
                          >
                            {person}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Source Links */}
                  {decision.sources && decision.sources.length > 0 && (
                    <div className="flex flex-wrap gap-2 pt-4 border-t border-navy-700">
                      {decision.sources.map((source, sidx) => (
                        <a
                          key={sidx}
                          href={source.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-lime-400 hover:underline flex items-center gap-1"
                        >
                          {source.type} <ExternalLink className="w-3 h-3" />
                        </a>
                      ))}
                    </div>
                  )}

                  {/* Related Project */}
                  {decision.projectName && (
                    <div className="mt-3 pt-3 border-t border-navy-700">
                      <span className="text-xs text-gray-500">Project: </span>
                      <span className="text-xs text-lime-400 font-medium">
                        {decision.projectName}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {decisions.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              No decisions found
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DecisionTimeline;
