import React, { useEffect, useRef, useState } from 'react';
import { Network } from 'vis-network';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_BASE || 'https://api.example.com';

const KnowledgeGraph = () => {
  const containerRef = useRef(null);
  const networkRef = useRef(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [dateRange, setDateRange] = useState({ start: '', end: '' });

  useEffect(() => {
    initializeGraph();
  }, []);

  const initializeGraph = async () => {
    // Sample data - replace with API call
    const nodes = [
      { id: 1, label: 'Platform Rebuild', group: 'project', color: '#84cc16' },
      { id: 2, label: 'Alice', group: 'person', color: '#3b82f6' },
      { id: 3, label: 'API Refactor', group: 'decision', color: '#f59e0b' },
      { id: 4, label: 'Email Thread', group: 'artifact', color: '#8b5cf6' },
      { id: 5, label: 'Commit abc123', group: 'event', color: '#ec4899' },
      { id: 6, label: 'Mobile App', group: 'project', color: '#84cc16' },
      { id: 7, label: 'Bob', group: 'person', color: '#3b82f6' },
    ];

    const edges = [
      { from: 1, to: 3, label: 'has_decision' },
      { from: 2, to: 3, label: 'made' },
      { from: 3, to: 4, label: 'triggered_by' },
      { from: 3, to: 5, label: 'implemented_in' },
      { from: 6, to: 7, label: 'has_member' },
    ];

    const data = { nodes, edges };

    const options = {
      nodes: {
        shape: 'dot',
        size: 20,
        font: {
          size: 14,
          color: '#e5e7eb',
        },
        borderWidth: 2,
        borderWidthSelected: 4,
      },
      edges: {
        width: 2,
        color: { color: '#4b5563', highlight: '#84cc16' },
        font: {
          size: 12,
          color: '#9ca3af',
          background: '#0f1f3a',
        },
        arrows: {
          to: { enabled: true, scaleFactor: 0.5 },
        },
      },
      physics: {
        stabilization: true,
        barnesHut: {
          gravitationalConstant: -2000,
          springConstant: 0.001,
          springLength: 200,
        },
      },
      interaction: {
        hover: true,
        tooltipDelay: 200,
      },
    };

    if (containerRef.current) {
      networkRef.current = new Network(containerRef.current, data, options);

      networkRef.current.on('click', async (params) => {
        if (params.nodes.length > 0) {
          const nodeId = params.nodes[0];
          const node = nodes.find(n => n.id === nodeId);
          setSelectedNode(node);
          
          // Fetch connected nodes
          try {
            const response = await axios.post(`${API_BASE}/graph`, {
              nodeId: nodeId,
              queryType: 'neighbors'
            });
            // Update graph with new data
          } catch (error) {
            console.error('Error fetching graph data:', error);
          }
        }
      });
    }
  };

  return (
    <div className="min-h-screen bg-navy-900 text-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-4xl font-mono font-bold text-lime-400">Knowledge Graph</h1>
          
          {/* Date Range Filter */}
          <div className="flex gap-3 items-center">
            <input
              type="date"
              value={dateRange.start}
              onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
              className="bg-navy-800 border border-navy-700 rounded-lg px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-lime-400"
            />
            <span className="text-gray-500">to</span>
            <input
              type="date"
              value={dateRange.end}
              onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
              className="bg-navy-800 border border-navy-700 rounded-lg px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-lime-400"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Graph Visualization */}
          <div className="lg:col-span-3 bg-navy-800 rounded-lg border border-navy-700 overflow-hidden">
            <div
              ref={containerRef}
              className="w-full h-[600px]"
              style={{ background: '#0f1f3a' }}
            />
          </div>

          {/* Node Details Panel */}
          <div className="bg-navy-800 rounded-lg p-6 border border-navy-700">
            <h2 className="text-xl font-mono font-semibold text-lime-400 mb-4">Node Details</h2>
            
            {selectedNode ? (
              <div className="space-y-4">
                <div>
                  <p className="text-xs text-gray-500 mb-1">Type</p>
                  <p className="text-sm font-semibold text-gray-300 capitalize">{selectedNode.group}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 mb-1">Label</p>
                  <p className="text-sm font-semibold text-gray-300">{selectedNode.label}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 mb-1">Connections</p>
                  <p className="text-sm font-semibold text-gray-300">5 nodes</p>
                </div>
                <button className="w-full bg-lime-400 text-navy-900 px-4 py-2 rounded-lg font-semibold hover:bg-lime-500 text-sm">
                  View Details
                </button>
              </div>
            ) : (
              <p className="text-sm text-gray-500">Click on a node to see details</p>
            )}

            {/* Legend */}
            <div className="mt-8 pt-6 border-t border-navy-700">
              <h3 className="text-sm font-semibold text-gray-400 mb-3">Legend</h3>
              <div className="space-y-2">
                {[
                  { color: '#84cc16', label: 'Project' },
                  { color: '#3b82f6', label: 'Person' },
                  { color: '#f59e0b', label: 'Decision' },
                  { color: '#8b5cf6', label: 'Artifact' },
                  { color: '#ec4899', label: 'Event' },
                ].map((item) => (
                  <div key={item.label} className="flex items-center gap-2">
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: item.color }}
                    />
                    <span className="text-xs text-gray-400">{item.label}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default KnowledgeGraph;
