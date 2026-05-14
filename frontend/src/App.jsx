import React, { useState, useEffect } from 'react';
import { Pill, Menu, Trash2 } from 'lucide-react';
import Sidebar from './components/Sidebar';
import ChatInterface from './components/ChatInterface';
import { fetchMemory, fetchChatHistory, clearMemory } from './api';

function App() {
  const [memory, setMemory] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [showClearModal, setShowClearModal] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  const loadData = async () => {
    const mem = await fetchMemory();
    setMemory(mem);
    const hist = await fetchChatHistory();
    setChatHistory(hist);
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleClear = async () => {
    await clearMemory();
    await loadData();
    setShowClearModal(false);
    setMenuOpen(false);
  };

  return (
    <div className="h-screen w-full flex flex-col overflow-hidden bg-medic-chatbg">
      {/* Topbar */}
      <header className="h-14 bg-medic-primary flex items-center justify-between px-4 md:px-6 shrink-0 shadow-sm relative z-20">
        <div className="flex items-center gap-3 text-white">
          <div className="bg-white/10 p-1.5 rounded-lg">
            <Pill size={20} className="text-white" />
          </div>
          <div className="flex items-baseline gap-2">
            <h1 className="font-bold text-lg tracking-tight">MaatharAI</h1>
            <span className="text-medic-accent text-sm font-medium hidden sm:inline">— Know before you take</span>
          </div>
        </div>
        
        <div className="relative">
          <button 
            onClick={() => setMenuOpen(!menuOpen)}
            className="flex items-center gap-2 px-3 py-1.5 bg-white/10 hover:bg-white/20 text-white rounded-full text-sm font-medium transition-colors"
          >
            <Menu size={16} />
            <span className="hidden sm:inline">Menu</span>
          </button>
          
          {menuOpen && (
            <div className="absolute right-0 top-full mt-2 w-48 bg-white rounded-xl shadow-xl border border-slate-100 py-1 overflow-hidden z-50">
              <button 
                onClick={() => setShowClearModal(true)}
                className="w-full text-left px-4 py-3 text-sm text-medic-severe hover:bg-slate-50 flex items-center gap-2 font-medium"
              >
                <Trash2 size={16} />
                Clear Memory
              </button>
            </div>
          )}
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 flex overflow-hidden">
        {/* Chat Interface */}
        <ChatInterface history={chatHistory} reloadData={loadData} />
        
        {/* Right Sidebar (Persistent on Desktop) */}
        <Sidebar memory={memory} />
      </main>

      {/* Clear Modal Dialog */}
      {showClearModal && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl w-full max-w-sm shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
            <div className="p-6">
              <h2 className="text-lg font-bold text-slate-800 mb-2">Clear all data?</h2>
              <p className="text-sm text-slate-600 leading-relaxed mb-6">
                This removes all saved medications, conditions, and chat history. This cannot be undone.
              </p>
              <div className="flex gap-3">
                <button 
                  onClick={() => setShowClearModal(false)}
                  className="flex-1 py-2.5 px-4 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
                >
                  Cancel
                </button>
                <button 
                  onClick={handleClear}
                  className="flex-1 py-2.5 px-4 text-sm font-medium text-white bg-medic-primary hover:bg-blue-600 rounded-xl transition-colors shadow-sm"
                >
                  Clear data
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
