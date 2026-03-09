import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_BASE || 'https://api.example.com';

const AskMemory = () => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hi! I\'m your Memory Assistant. Ask me anything about your projects, decisions, or past discussions. For example: "Why was Feature X delayed in March?"'
    }
  ]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSearch = async () => {
    if (!query.trim() || loading) return;
    
    const userMessage = query.trim();
    setQuery('');
    
    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);
    
    try {
      const response = await axios.post(`${API_BASE}/query`, { query: userMessage });
      
      // Add assistant response
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.data.answer || 'I couldn\'t find relevant information to answer that question.',
        sources: response.data.sources,
        confidence: response.data.confidence
      }]);
    } catch (error) {
      console.error('Query error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        error: true
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-navy-900 text-gray-100">
      {/* Header */}
      <div className="bg-navy-800 border-b border-navy-700 p-4">
        <h1 className="text-2xl font-mono font-bold text-lime-400">Memory Assistant</h1>
        <p className="text-sm text-gray-400 mt-1">Ask questions about your projects and decisions</p>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, idx) => (
          <div
            key={idx}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-3xl rounded-lg p-4 ${
                message.role === 'user'
                  ? 'bg-lime-400 text-navy-900'
                  : message.error
                  ? 'bg-red-900/20 border border-red-500 text-red-400'
                  : 'bg-navy-800 border border-navy-700 text-gray-100'
              }`}
            >
              {/* Message Content */}
              <div className="whitespace-pre-wrap leading-relaxed">
                {message.content}
              </div>

              {/* Sources (for assistant messages) */}
              {message.sources && message.sources.length > 0 && (
                <div className="mt-4 pt-4 border-t border-navy-700">
                  <div className="text-xs font-semibold text-lime-400 mb-2">
                    Sources ({message.sources.length})
                  </div>
                  <div className="space-y-2">
                    {message.sources.slice(0, 3).map((source, sidx) => (
                      <div key={sidx} className="text-xs text-gray-400 flex items-start gap-2">
                        <span className="text-lime-400 font-mono">[{sidx + 1}]</span>
                        <div>
                          <span className="capitalize">{source.type}</span>
                          {source.timestamp && (
                            <span className="ml-2">
                              • {new Date(source.timestamp).toLocaleDateString()}
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Confidence Score */}
              {message.confidence !== undefined && message.confidence > 0 && (
                <div className="mt-2 text-xs text-gray-500">
                  Confidence: {message.confidence}%
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
                <span>Thinking...</span>
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
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSearch()}
              placeholder="Ask about your projects, decisions, or discussions..."
              disabled={loading}
              className="flex-1 bg-navy-700 border border-navy-600 rounded-lg px-4 py-3 text-gray-100 placeholder-gray-500 focus:outline-none focus:border-lime-400 disabled:opacity-50"
            />
            <button
              onClick={handleSearch}
              disabled={loading || !query.trim()}
              className="bg-lime-400 text-navy-900 px-6 py-3 rounded-lg font-semibold hover:bg-lime-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
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

export default AskMemory;
