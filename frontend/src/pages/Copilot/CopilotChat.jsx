import React, { useState, useEffect, useRef } from 'react';
import api from '../../services/api';
import Breadcrumb from '../../components/Common/Breadcrumb';
import {
  Sparkles,
  Send,
  MessageSquare,
  Plus,
  Trash2,
  Pin,
  Clock,
  CheckCircle2,
  Cpu,
  BookOpen,
  Wrench,
  Bot,
  User,
  ShieldCheck,
  Zap,
  ChevronRight,
  Code2
} from 'lucide-react';

export default function CopilotChat() {
  const [conversations, setConversations] = useState([]);
  const [activeConvId, setActiveConvId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [streamStep, setStreamStep] = useState(null);
  const chatEndRef = useRef(null);

  useEffect(() => {
    fetchConversations();
  }, []);

  const fetchConversations = async () => {
    try {
      const res = await api.get('/copilot/conversations');
      const convList = res.data.conversations || [];
      setConversations(convList);
      if (convList.length > 0 && !activeConvId) {
        loadConversation(convList[0].id);
      }
    } catch (err) {
      console.error("Failed to load conversations:", err);
    }
  };

  const loadConversation = async (convId) => {
    setActiveConvId(convId);
    try {
      const res = await api.get(`/copilot/conversations/${convId}`);
      setMessages(res.data.messages || []);
    } catch (err) {
      console.error("Failed to load conversation details:", err);
    }
  };

  const handleStartNewChat = () => {
    setActiveConvId(null);
    setMessages([]);
  };

  const handleDeleteChat = async (e, convId) => {
    e.stopPropagation();
    try {
      await api.delete(`/copilot/conversations/${convId}`);
      if (activeConvId === convId) handleStartNewChat();
      fetchConversations();
    } catch (err) {
      alert("Failed to delete conversation");
    }
  };

  const handleSendQuery = async (queryText) => {
    const q = queryText || inputQuery;
    if (!q.trim() || loading) return;

    const tempUserMsg = { id: Date.now(), role: 'user', content: q };
    setMessages(prev => [...prev, tempUserMsg]);
    setInputQuery('');
    setLoading(true);

    // Simulate Streaming Step Feed
    setStreamStep("Evaluating query context & routing to Multi-Agent framework...");

    try {
      const userStr = JSON.parse(localStorage.getItem('user') || '{}');
      const userId = userStr.id || "admin_user_id";

      const res = await api.post('/copilot/chat', {
        query: q,
        user_id: userId,
        conversation_id: activeConvId
      });

      if (!activeConvId) {
        setActiveConvId(res.data.conversation_id);
        fetchConversations();
      }

      const assistantMsg = {
        id: Date.now() + 1,
        role: 'assistant',
        content: res.data.assistant_message,
        sources: res.data.explainability?.sources,
        agents_executed: res.data.explainability?.agents_executed,
        confidence_score: res.data.explainability?.confidence_score,
        tool_calls: res.data.explainability?.tool_calls,
        total_time_ms: res.data.explainability?.profiling_ms?.total_time
      };

      setMessages(prev => [...prev, assistantMsg]);
    } catch (err) {
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: 'assistant',
        content: "Error: " + (err.response?.data?.message || err.message)
      }]);
    } finally {
      setLoading(false);
      setStreamStep(null);
      chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <Breadcrumb items={[{ label: "Copilot" }, { label: "AI Integration Assistant" }]} />
          <h1 className="text-2xl font-black text-gray-900 dark:text-gray-100 flex items-center">
            <Sparkles className="w-6 h-6 text-purple-600 mr-2" /> AI Integration Copilot & Multi-Agent Assistant
          </h1>
        </div>
      </div>

      {/* Main Studio Workbench Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[720px]">
        {/* Left Column: Conversation History Sidebar */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm p-4 flex flex-col justify-between">
          <div className="space-y-4">
            <button
              onClick={handleStartNewChat}
              className="w-full py-2.5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white font-bold text-xs rounded-xl shadow transition-all flex items-center justify-center space-x-2"
            >
              <Plus className="w-4 h-4" />
              <span>New Copilot Session</span>
            </button>

            <div className="space-y-1 overflow-y-auto max-h-[580px]">
              <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400">Past Conversations</span>
              {conversations.map(c => (
                <div
                  key={c.id}
                  onClick={() => loadConversation(c.id)}
                  className={`p-3 rounded-xl cursor-pointer text-xs flex justify-between items-center transition-colors ${
                    activeConvId === c.id ? 'bg-purple-50 dark:bg-purple-950/40 text-purple-700 dark:text-purple-300 font-bold border border-purple-200 dark:border-purple-800' : 'hover:bg-gray-50 text-gray-700 dark:text-gray-300'
                  }`}
                >
                  <div className="flex items-center space-x-2 truncate">
                    <MessageSquare className="w-3.5 h-3.5 flex-shrink-0" />
                    <span className="truncate">{c.title}</span>
                  </div>
                  <button onClick={(e) => handleDeleteChat(e, c.id)} className="text-gray-400 hover:text-red-500">
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right 3 Columns: Active Chat Workbench */}
        <div className="lg:col-span-3 bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm flex flex-col justify-between p-4">
          
          {/* Chat Feed */}
          <div className="flex-1 overflow-y-auto space-y-4 p-2 max-h-[560px]">
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center space-y-4 text-center text-gray-400">
                <Bot className="w-12 h-12 text-purple-500 opacity-80 animate-bounce" />
                <div>
                  <h3 className="font-bold text-sm text-gray-800 dark:text-gray-200">How can I assist your integration pipeline today?</h3>
                  <p className="text-xs text-gray-500">Ask about SOAP conversions, execution errors, mapping rules, or performance tuning.</p>
                </div>

                {/* Preset Prompt Chips */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-left max-w-lg pt-2">
                  {[
                    "Why did my SOAP integration fail?",
                    "Generate mapping rules between SOAP and REST JSON",
                    "Explain payload schema validation error ERR_VAL_001",
                    "Recommend performance latency optimizations"
                  ].map((preset, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSendQuery(preset)}
                      className="p-3 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 hover:border-purple-400 text-xs text-gray-700 dark:text-gray-300 font-medium rounded-xl text-left transition-colors"
                    >
                      {preset}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              messages.map(msg => (
                <div key={msg.id} className={`flex space-x-3 text-xs ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  {msg.role !== 'user' && (
                    <div className="w-7 h-7 rounded-xl bg-purple-600 text-white flex items-center justify-center font-bold flex-shrink-0">
                      <Bot className="w-4 h-4" />
                    </div>
                  )}

                  <div className={`max-w-2xl p-4 rounded-2xl space-y-3 ${
                    msg.role === 'user' ? 'bg-indigo-600 text-white font-medium rounded-br-none' : 'bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 border border-gray-200 dark:border-gray-700 rounded-bl-none'
                  }`}>
                    <p className="whitespace-pre-wrap font-sans text-xs leading-relaxed">{msg.content}</p>

                    {/* Explainability Badges & Citations */}
                    {msg.role === 'assistant' && (
                      <div className="pt-2 border-t border-gray-200 dark:border-gray-800 space-y-2 text-[11px]">
                        <div className="flex flex-wrap items-center gap-2">
                          {msg.confidence_score && (
                            <span className="px-2 py-0.5 bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 font-bold rounded-md flex items-center">
                              <ShieldCheck className="w-3 h-3 mr-1" /> {(msg.confidence_score * 100).toFixed(0)}% Confidence
                            </span>
                          )}

                          {msg.total_time_ms && (
                            <span className="px-2 py-0.5 bg-purple-100 dark:bg-purple-950 text-purple-700 dark:text-purple-300 font-mono font-bold rounded-md flex items-center">
                              <Clock className="w-3 h-3 mr-1" /> {msg.total_time_ms} ms
                            </span>
                          )}
                        </div>

                        {msg.agents_executed?.length > 0 && (
                          <div className="flex items-center space-x-1.5 text-gray-500">
                            <Cpu className="w-3 h-3 text-indigo-500" />
                            <span>Executed Agents: <strong>{msg.agents_executed.join(', ')}</strong></span>
                          </div>
                        )}

                        {msg.sources?.length > 0 && (
                          <div className="flex items-center space-x-1.5 text-gray-500">
                            <BookOpen className="w-3 h-3 text-amber-500" />
                            <span>Sources Cited: <strong>{msg.sources.join(', ')}</strong></span>
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  {msg.role === 'user' && (
                    <div className="w-7 h-7 rounded-xl bg-indigo-600 text-white flex items-center justify-center font-bold flex-shrink-0">
                      <User className="w-4 h-4" />
                    </div>
                  )}
                </div>
              ))
            )}

            {/* Real-time Streaming State Indicator */}
            {loading && streamStep && (
              <div className="p-3 bg-purple-50 dark:bg-purple-950/40 border border-purple-200 dark:border-purple-800 rounded-xl text-xs text-purple-700 dark:text-purple-300 flex items-center space-x-2 animate-pulse">
                <Sparkles className="w-4 h-4" />
                <span className="font-bold">{streamStep}</span>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Prompt Input Box */}
          <div className="pt-3 border-t border-gray-100 dark:border-gray-700 flex items-center space-x-2">
            <input
              type="text"
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSendQuery()}
              placeholder="Ask Copilot about schemas, mappings, errors, or performance..."
              className="flex-1 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-4 py-3 text-xs font-medium focus:outline-none focus:border-purple-500 text-gray-900 dark:text-gray-100"
            />
            <button
              onClick={() => handleSendQuery()}
              disabled={loading || !inputQuery.trim()}
              className="px-5 py-3 bg-purple-600 hover:bg-purple-700 text-white font-bold text-xs rounded-xl shadow transition-colors flex items-center space-x-1.5 disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
              <span>Send</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
