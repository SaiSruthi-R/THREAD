import React, { useState, useEffect } from 'react';
import { FolderKanban, Users, Brain, TrendingUp, X, Trash2, BarChart3, Upload, File, Download } from 'lucide-react';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_BASE || 'https://api.example.com';

const ProjectsView = () => {
  const [projects, setProjects] = useState([]);
  const [filter, setFilter] = useState('all');
  const [sortBy, setSortBy] = useState('name');
  const [showModal, setShowModal] = useState(false);
  const [showPlotModal, setShowPlotModal] = useState(false);
  const [showFilesModal, setShowFilesModal] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);
  const [projectFiles, setProjectFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [newProject, setNewProject] = useState({
    name: '',
    description: '',
    status: 'planning',
    members: []
  });

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const response = await axios.get(`${API_BASE}/projects`);
      setProjects(response.data.projects || []);
    } catch (error) {
      console.error('Error fetching projects:', error);
    }
  };

  const handleCreateProject = async () => {
    try {
      await axios.post(`${API_BASE}/projects`, newProject);
      setShowModal(false);
      setNewProject({ name: '', description: '', status: 'planning', members: [] });
      fetchProjects();
    } catch (error) {
      console.error('Error creating project:', error);
      alert('Failed to create project. Please try again.');
    }
  };

  const handleDeleteProject = async (projectId, projectName) => {
    if (window.confirm(`Are you sure you want to delete "${projectName}"? This action cannot be undone.`)) {
      try {
        await axios.delete(`${API_BASE}/projects/${projectId}`);
        fetchProjects();
      } catch (error) {
        console.error('Error deleting project:', error);
        alert('Failed to delete project. Please try again.');
      }
    }
  };

  const handleViewFiles = async (project) => {
    setSelectedProject(project);
    setShowFilesModal(true);
    await fetchProjectFiles(project.projectId);
  };

  const fetchProjectFiles = async (projectId) => {
    try {
      const response = await axios.get(`${API_BASE}/files/project/${projectId}`);
      setProjectFiles(response.data.files || []);
    } catch (error) {
      console.error('Error fetching files:', error);
      setProjectFiles([]);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file || !selectedProject) return;

    setUploading(true);
    try {
      // Read file as base64
      const reader = new FileReader();
      reader.onload = async (e) => {
        const base64Content = e.target.result.split(',')[1];
        
        await axios.post(`${API_BASE}/files`, {
          projectId: selectedProject.projectId,
          fileName: file.name,
          fileContent: base64Content,
          fileType: file.type,
          description: `Uploaded to ${selectedProject.name}`
        });

        // Refresh file list
        await fetchProjectFiles(selectedProject.projectId);
        setUploading(false);
        event.target.value = ''; // Reset input
      };
      reader.readAsDataURL(file);
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('Failed to upload file. Please try again.');
      setUploading(false);
    }
  };

  const handleDeleteFile = async (fileId, fileName) => {
    if (window.confirm(`Are you sure you want to delete "${fileName}"?`)) {
      try {
        await axios.delete(`${API_BASE}/files/${fileId}`);
        await fetchProjectFiles(selectedProject.projectId);
      } catch (error) {
        console.error('Error deleting file:', error);
        alert('Failed to delete file. Please try again.');
      }
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const filteredProjects = projects
    .filter(p => filter === 'all' || p.status === filter)
    .sort((a, b) => {
      if (sortBy === 'name') return a.name.localeCompare(b.name);
      if (sortBy === 'progress') return (b.progress || 0) - (a.progress || 0);
      return 0;
    });

  return (
    <div className="min-h-screen bg-navy-900 text-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-mono font-bold text-lime-400">Projects</h1>
          <div className="flex gap-3">
            <button 
              onClick={() => setShowPlotModal(true)}
              className="bg-blue-500 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-600 flex items-center gap-2"
            >
              <BarChart3 className="w-5 h-5" />
              View Analytics
            </button>
            <button 
              onClick={() => setShowModal(true)}
              className="bg-lime-400 text-navy-900 px-6 py-2 rounded-lg font-semibold hover:bg-lime-500"
            >
              + New Project
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="flex gap-4 mb-8">
          <div className="flex gap-2">
            <span className="text-gray-400 text-sm self-center">Filter:</span>
            {['all', 'active', 'planning', 'completed'].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                  filter === f
                    ? 'bg-lime-400 text-navy-900'
                    : 'bg-navy-800 text-gray-400 hover:bg-navy-700'
                }`}
              >
                {f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            ))}
          </div>
          <div className="flex gap-2 ml-auto">
            <span className="text-gray-400 text-sm self-center">Sort:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="bg-navy-800 border border-navy-700 rounded-lg px-4 py-2 text-sm text-gray-300 focus:outline-none focus:border-lime-400"
            >
              <option value="name">Name</option>
              <option value="progress">Progress</option>
            </select>
          </div>
        </div>

        {/* Project Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProjects.map((project) => (
            <div
              key={project.projectId}
              className="bg-navy-800 rounded-lg p-6 border border-navy-700 hover:border-lime-400 transition"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <FolderKanban className="text-lime-400" />
                  <h3 className="text-xl font-semibold text-gray-100">{project.name}</h3>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-3 py-1 text-xs rounded-full font-medium ${
                    project.status === 'active' ? 'bg-lime-500 text-navy-900' :
                    project.status === 'planning' ? 'bg-blue-500 text-white' :
                    'bg-gray-600 text-gray-200'
                  }`}>
                    {project.status}
                  </span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteProject(project.projectId, project.name);
                    }}
                    className="p-2 text-red-400 hover:text-red-300 hover:bg-red-900/20 rounded-lg transition"
                    title="Delete project"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              <p className="text-gray-400 text-sm mb-4 line-clamp-2">
                {project.description || 'No description available'}
              </p>

              {/* Progress Bar */}
              <div className="mb-4">
                <div className="flex justify-between text-xs text-gray-400 mb-1">
                  <span>Progress</span>
                  <span>{project.progress || 0}%</span>
                </div>
                <div className="w-full bg-navy-900 rounded-full h-2">
                  <div
                    className="bg-lime-400 h-2 rounded-full transition-all"
                    style={{ width: `${project.progress || 0}%` }}
                  />
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-4 pt-4 border-t border-navy-700">
                <div className="text-center">
                  <Users className="w-4 h-4 text-gray-400 mx-auto mb-1" />
                  <p className="text-sm font-semibold text-gray-300">{project.members?.length || 0}</p>
                  <p className="text-xs text-gray-500">Members</p>
                </div>
                <div className="text-center">
                  <Brain className="w-4 h-4 text-gray-400 mx-auto mb-1" />
                  <p className="text-sm font-semibold text-gray-300">{project.decisionCount || 0}</p>
                  <p className="text-xs text-gray-500">Decisions</p>
                </div>
                <div className="text-center">
                  <TrendingUp className="w-4 h-4 text-gray-400 mx-auto mb-1" />
                  <p className="text-sm font-semibold text-gray-300">{project.knowledgeItemCount || 0}</p>
                  <p className="text-xs text-gray-500">Items</p>
                </div>
              </div>

              {/* View Files Button */}
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleViewFiles(project);
                }}
                className="w-full mt-4 bg-blue-500 text-white px-4 py-2 rounded-lg font-semibold hover:bg-blue-600 flex items-center justify-center gap-2"
              >
                <Upload className="w-4 h-4" />
                Manage Files
              </button>
            </div>
          ))}
        </div>

        {filteredProjects.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            No projects found
          </div>
        )}
      </div>

      {/* New Project Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-navy-800 rounded-lg p-6 max-w-md w-full mx-4 border border-navy-700">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-mono font-bold text-lime-400">New Project</h2>
              <button 
                onClick={() => setShowModal(false)}
                className="text-gray-400 hover:text-gray-300"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Project Name *
                </label>
                <input
                  type="text"
                  value={newProject.name}
                  onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                  placeholder="Enter project name"
                  className="w-full bg-navy-700 border border-navy-600 rounded-lg px-4 py-2 text-gray-100 placeholder-gray-500 focus:outline-none focus:border-lime-400"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Description
                </label>
                <textarea
                  value={newProject.description}
                  onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                  placeholder="Enter project description"
                  rows={3}
                  className="w-full bg-navy-700 border border-navy-600 rounded-lg px-4 py-2 text-gray-100 placeholder-gray-500 focus:outline-none focus:border-lime-400 resize-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Status
                </label>
                <select
                  value={newProject.status}
                  onChange={(e) => setNewProject({ ...newProject, status: e.target.value })}
                  className="w-full bg-navy-700 border border-navy-600 rounded-lg px-4 py-2 text-gray-100 focus:outline-none focus:border-lime-400"
                >
                  <option value="planning">Planning</option>
                  <option value="active">Active</option>
                  <option value="completed">Completed</option>
                </select>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  onClick={() => setShowModal(false)}
                  className="flex-1 bg-navy-700 text-gray-300 px-4 py-2 rounded-lg font-semibold hover:bg-navy-600"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreateProject}
                  disabled={!newProject.name.trim()}
                  className="flex-1 bg-lime-400 text-navy-900 px-4 py-2 rounded-lg font-semibold hover:bg-lime-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Create Project
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Project Analytics Modal */}
      {showPlotModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-navy-800 rounded-lg p-6 max-w-4xl w-full mx-4 border border-navy-700 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-mono font-bold text-lime-400">Project Analytics</h2>
              <button 
                onClick={() => setShowPlotModal(false)}
                className="text-gray-400 hover:text-gray-300"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Summary Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-navy-700 rounded-lg p-4 border border-navy-600">
                <p className="text-gray-400 text-sm mb-1">Total Projects</p>
                <p className="text-3xl font-bold text-lime-400">{projects.length}</p>
              </div>
              <div className="bg-navy-700 rounded-lg p-4 border border-navy-600">
                <p className="text-gray-400 text-sm mb-1">Active</p>
                <p className="text-3xl font-bold text-blue-400">
                  {projects.filter(p => p.status === 'active').length}
                </p>
              </div>
              <div className="bg-navy-700 rounded-lg p-4 border border-navy-600">
                <p className="text-gray-400 text-sm mb-1">Planning</p>
                <p className="text-3xl font-bold text-yellow-400">
                  {projects.filter(p => p.status === 'planning').length}
                </p>
              </div>
              <div className="bg-navy-700 rounded-lg p-4 border border-navy-600">
                <p className="text-gray-400 text-sm mb-1">Completed</p>
                <p className="text-3xl font-bold text-green-400">
                  {projects.filter(p => p.status === 'completed').length}
                </p>
              </div>
            </div>

            {/* Progress Chart */}
            <div className="bg-navy-700 rounded-lg p-6 border border-navy-600 mb-6">
              <h3 className="text-lg font-semibold text-gray-100 mb-4">Project Progress Overview</h3>
              <div className="space-y-4">
                {projects.map((project) => (
                  <div key={project.projectId}>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-gray-300 font-medium">{project.name}</span>
                      <span className="text-gray-400">{project.progress || 0}%</span>
                    </div>
                    <div className="w-full bg-navy-900 rounded-full h-3">
                      <div
                        className={`h-3 rounded-full transition-all ${
                          project.status === 'completed' ? 'bg-green-500' :
                          project.status === 'active' ? 'bg-lime-400' :
                          'bg-blue-500'
                        }`}
                        style={{ width: `${project.progress || 0}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Status Distribution Chart */}
            <div className="bg-navy-700 rounded-lg p-6 border border-navy-600 mb-6">
              <h3 className="text-lg font-semibold text-gray-100 mb-4">Status Distribution</h3>
              <div className="flex items-end justify-around h-64 gap-4">
                {['planning', 'active', 'completed'].map((status) => {
                  const count = projects.filter(p => p.status === status).length;
                  const maxCount = Math.max(
                    projects.filter(p => p.status === 'planning').length,
                    projects.filter(p => p.status === 'active').length,
                    projects.filter(p => p.status === 'completed').length,
                    1
                  );
                  const height = (count / maxCount) * 100;
                  
                  return (
                    <div key={status} className="flex flex-col items-center flex-1">
                      <div className="w-full flex items-end justify-center h-48">
                        <div
                          className={`w-full rounded-t-lg transition-all ${
                            status === 'planning' ? 'bg-blue-500' :
                            status === 'active' ? 'bg-lime-400' :
                            'bg-green-500'
                          }`}
                          style={{ height: `${height}%` }}
                        >
                          <div className="text-center pt-2 font-bold text-navy-900">
                            {count}
                          </div>
                        </div>
                      </div>
                      <p className="text-gray-300 text-sm mt-2 capitalize">{status}</p>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Activity Metrics */}
            <div className="bg-navy-700 rounded-lg p-6 border border-navy-600">
              <h3 className="text-lg font-semibold text-gray-100 mb-4">Activity Metrics</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">Total Decisions</span>
                  <span className="text-lime-400 font-bold text-xl">
                    {projects.reduce((sum, p) => sum + (p.decisionCount || 0), 0)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">Total Knowledge Items</span>
                  <span className="text-lime-400 font-bold text-xl">
                    {projects.reduce((sum, p) => sum + (p.knowledgeItemCount || 0), 0)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">Total Team Members</span>
                  <span className="text-lime-400 font-bold text-xl">
                    {projects.reduce((sum, p) => sum + (p.members?.length || 0), 0)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">Average Progress</span>
                  <span className="text-lime-400 font-bold text-xl">
                    {projects.length > 0 
                      ? Math.round(projects.reduce((sum, p) => sum + (p.progress || 0), 0) / projects.length)
                      : 0}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Project Files Modal */}
      {showFilesModal && selectedProject && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-navy-800 rounded-lg p-6 max-w-4xl w-full mx-4 border border-navy-700 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <div>
                <h2 className="text-2xl font-mono font-bold text-lime-400">Project Files</h2>
                <p className="text-gray-400 text-sm mt-1">{selectedProject.name}</p>
              </div>
              <button 
                onClick={() => {
                  setShowFilesModal(false);
                  setSelectedProject(null);
                  setProjectFiles([]);
                }}
                className="text-gray-400 hover:text-gray-300"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Upload Section */}
            <div className="bg-navy-700 rounded-lg p-6 border border-navy-600 mb-6">
              <h3 className="text-lg font-semibold text-gray-100 mb-4 flex items-center gap-2">
                <Upload className="w-5 h-5 text-lime-400" />
                Upload Files
              </h3>
              <div className="flex items-center gap-4">
                <label className="flex-1 cursor-pointer">
                  <div className="border-2 border-dashed border-navy-600 rounded-lg p-8 text-center hover:border-lime-400 transition">
                    <Upload className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                    <p className="text-gray-300 font-medium mb-1">
                      {uploading ? 'Uploading...' : 'Click to upload or drag and drop'}
                    </p>
                    <p className="text-gray-500 text-sm">
                      Documents, images, code files, etc.
                    </p>
                  </div>
                  <input
                    type="file"
                    onChange={handleFileUpload}
                    disabled={uploading}
                    className="hidden"
                  />
                </label>
              </div>
            </div>

            {/* Files List */}
            <div className="bg-navy-700 rounded-lg p-6 border border-navy-600">
              <h3 className="text-lg font-semibold text-gray-100 mb-4 flex items-center gap-2">
                <File className="w-5 h-5 text-lime-400" />
                Files ({projectFiles.length})
              </h3>
              
              {projectFiles.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <File className="w-16 h-16 mx-auto mb-3 opacity-50" />
                  <p>No files uploaded yet</p>
                  <p className="text-sm mt-1">Upload your first file to get started</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {projectFiles.map((file) => (
                    <div
                      key={file.entityId}
                      className="flex items-center justify-between bg-navy-800 rounded-lg p-4 border border-navy-600 hover:border-lime-400 transition"
                    >
                      <div className="flex items-center gap-3 flex-1">
                        <File className="w-8 h-8 text-lime-400" />
                        <div className="flex-1 min-w-0">
                          <p className="text-gray-100 font-medium truncate">{file.fileName}</p>
                          <div className="flex items-center gap-3 text-sm text-gray-400 mt-1">
                            <span>{formatFileSize(file.fileSize || 0)}</span>
                            <span>•</span>
                            <span>{new Date(file.uploadedAt).toLocaleDateString()}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {file.downloadUrl && (
                          <a
                            href={file.downloadUrl}
                            download={file.fileName}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="p-2 text-blue-400 hover:text-blue-300 hover:bg-blue-900/20 rounded-lg transition"
                            title="Download file"
                          >
                            <Download className="w-5 h-5" />
                          </a>
                        )}
                        <button
                          onClick={() => handleDeleteFile(file.entityId, file.fileName)}
                          className="p-2 text-red-400 hover:text-red-300 hover:bg-red-900/20 rounded-lg transition"
                          title="Delete file"
                        >
                          <Trash2 className="w-5 h-5" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProjectsView;
