import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Code, FileCode, Layers, CheckCircle } from 'lucide-react';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_BASE || 'https://api.example.com';

const AIAssistant = () => {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hi! I\'m your AI Development Assistant. I can help you with:\n\n• Code Review - Analyze your code for improvements\n• Architecture Suggestions - Design scalable systems\n• Code Generation - Create production-ready code\n• Project Upscaling - Expand your project scope\n\nWhat would you like help with today?'
    }
  ]);
  const [activeTab, setActiveTab] = useState('review');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async () => {
    if (!input.trim() || loading) return;
    
    const userMessage = input.trim();
    setInput('');
    
    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);
    
    try {
      let response;
      
      if (activeTab === 'review') {
        response = await axios.post(`${API_BASE}/ai-assistant`, {
          action: 'review',
          code: userMessage
        });
      } else if (activeTab === 'architecture') {
        response = await axios.post(`${API_BASE}/ai-assistant`, {
          action: 'architecture',
          requirements: userMessage
        });
      } else if (activeTab === 'generate') {
        response = await axios.post(`${API_BASE}/ai-assistant`, {
          action: 'generate_code',
          requirements: userMessage,
          language: 'python'
        });
      } else if (activeTab === 'upscale') {
        response = await axios.post(`${API_BASE}/ai-assistant`, {
          action: 'upscale',
          currentScope: userMessage,
          goals: ['scalability', 'performance']
        });
      }
      
      // Add assistant response
      const content = response.data.recommendations || 
                     response.data.suggestions || 
                     response.data.review || 
                     response.data.code ||
                     JSON.stringify(response.data, null, 2);
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: content,
        type: activeTab
      }]);
    } catch (error) {
      console.error('AI Assistant error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        error: true
      }]);
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'review', label: 'Code Review', icon: CheckCircle },
    { id: 'architecture', label: 'Architecture', icon: Layers },
    { id: 'generate', label: 'Generate Code', icon: Code },
    { id: 'upscale', label: 'Upscale Project', icon: FileCode }
  ];

  const getPlaceholder = () => {
    switch (activeTab) {
      case 'review':
        return 'Paste your code here for review...';
      case 'architecture':
        return 'Describe your system requirements...';
      case 'generate':
        return 'Describe what code you need...';
      case 'upscale':
        return 'Describe your current project scope...';
      default:
        return 'Type your message...';
    }
  };

  return (
    <div className="flex flex-col h-screen bg-navy-900 text-gray-100">
      {/* Header */}
      <div className="bg-navy-800 border-b border-navy-700 p-4">
        <h1 className="text-2xl font-mono font-bold text-lime-400">AI Development Assistant</h1>
        <p className="text-sm text-gray-400 mt-1">Powered by Meta Llama 3</p>
      </div>

      {/* Tabs */}
      <div className="bg-navy-800 border-b border-navy-700 px-4">
        <div className="flex gap-2 overflow-x-auto">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-3 border-b-2 transition whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'border-lime-400 text-lime-400'
                    : 'border-transparent text-gray-400 hover:text-gray-300'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="text-sm font-medium">{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, idx) => (
          <div
            key={idx}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-4xl rounded-lg p-4 ${
                message.role === 'user'
                  ? 'bg-lime-400 text-navy-900'
                  : message.error
                  ? 'bg-red-900/20 border border-red-500 text-red-400'
                  : 'bg-navy-800 border border-navy-700 text-gray-100'
              }`}
            >
              {/* Message Content */}
              <div className="whitespace-pre-wrap leading-relaxed font-mono text-sm">
                {message.content}
              </div>

              {/* Type Badge */}
              {message.type && (
                <div className="mt-2 inline-block px-2 py-1 bg-navy-700 rounded text-xs text-lime-400">
                  {message.type}
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Loading Indicator */}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-navy-800 border border-navy-700 rounded-lg p-4">
              <div className="flex items-center gap-2 text-gray-400">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Analyzing...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-navy-800 border-t border-navy-700 p-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex gap-2">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit();
                }
              }}
              placeholder={getPlaceholder()}
              disabled={loading}
              rows={3}
              className="flex-1 bg-navy-700 border border-navy-600 rounded-lg px-4 py-3 text-gray-100 placeholder-gray-500 focus:outline-none focus:border-lime-400 disabled:opacity-50 resize-none font-mono text-sm"
            />
            <button
              onClick={handleSubmit}
              disabled={loading || !input.trim()}
              className="bg-lime-400 text-navy-900 px-6 py-3 rounded-lg font-semibold hover:bg-lime-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 self-end"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
          <div className="mt-2 text-xs text-gray-500 text-center">
            Press Enter to send • Shift+Enter for new line
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIAssistant;
