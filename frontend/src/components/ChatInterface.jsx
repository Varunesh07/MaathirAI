import React, { useState, useRef, useEffect } from 'react';
import { Paperclip, Send, Loader2, FileImage, Bot, User } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { uploadFile, sendMessage } from '../api';

export default function ChatInterface({ history, reloadData }) {
  const [input, setInput] = useState('');
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingText, setLoadingText] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [history, loading]);

  const handleFileSelect = (e) => {
    if (e.target.files) {
      const selected = Array.from(e.target.files);
      setFiles(prev => {
        const combined = [...prev, ...selected];
        if (combined.length > 3) {
          alert("Maximum of 3 files can be uploaded at a time.");
          return combined.slice(0, 3);
        }
        return combined;
      });
    }
    // Reset value so picking the same file again works
    if (e.target) e.target.value = null;
  };

  const removeFile = (index) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const handleSend = async () => {
    if (!input.trim() && files.length === 0) return;
    
    setLoading(true);
    try {
      if (files.length > 0) {
        // Sequential smart upload logic
        for (let i = 0; i < files.length; i++) {
          setLoadingText(`Analyzing file ${i + 1} of ${files.length}...`);
          const isLast = i === files.length - 1;
          const msg = isLast ? input : null; // Only send the user's text message with the LAST file
          await uploadFile(files[i], msg, !isLast);
          await reloadData(); // Update UI after each file to show progress!
        }
      } else {
        setLoadingText('Thinking...');
        await sendMessage(input);
        await reloadData();
      }
    } catch (err) {
      console.error(err);
      alert('Error communicating with server.');
    } finally {
      setLoading(false);
      setLoadingText('');
      setInput('');
      setFiles([]);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-medic-chatbg relative">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6">
        {history.length === 0 && (
          <div className="bg-white border border-medic-border rounded-xl p-6 max-w-sm shadow-sm">
            <p className="text-slate-800 text-sm leading-relaxed">
              Hello! Upload a prescription, medicine strip, or medical report — or just ask me anything about your medicines.
            </p>
          </div>
        )}

        {history.map((msg, i) => {
          const isUser = msg.role === 'user';
          if (msg.role === 'system') return null; // Fallback in case API returns it

          if (isUser && msg.message.startsWith('[FILE:') && msg.message.endsWith(']')) {
            const filename = msg.message.slice(6, -1).trim();
            return (
              <div key={i} className="flex justify-end">
                <div className="bg-medic-deep text-medic-accent px-4 py-2.5 rounded-2xl rounded-br-sm text-sm font-medium shadow-sm flex items-center gap-2">
                  <FileImage size={16} />
                  {filename}
                </div>
              </div>
            );
          }

          return (
            <div key={i} className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] md:max-w-[75%] rounded-2xl p-4 shadow-sm ${
                isUser 
                  ? 'bg-medic-primary text-white rounded-br-sm' 
                  : 'bg-white border border-medic-border text-slate-800 rounded-bl-sm'
              }`}>
                <div className="prose prose-sm max-w-none prose-p:leading-relaxed">
                   <ReactMarkdown>{msg.message}</ReactMarkdown>
                </div>
              </div>
            </div>
          );
        })}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border border-medic-border rounded-2xl rounded-bl-sm p-4 shadow-sm flex items-center gap-3">
              <Loader2 className="animate-spin text-medic-accent" size={20} />
              <span className="text-sm text-slate-600 font-medium">{loadingText}</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-white border-t border-medic-border shrink-0">
        <div className="max-w-4xl mx-auto">
          {files.length > 0 && (
            <div className="flex gap-2 mb-3 overflow-x-auto pb-2">
              {files.map((file, i) => (
                <div key={i} className="flex items-center gap-2 bg-medic-deep text-medic-accent px-3 py-1.5 rounded-full text-xs font-medium shrink-0 group">
                  <FileImage size={14} />
                  <span className="max-w-[100px] truncate">{file.name}</span>
                  <button onClick={() => removeFile(i)} className="hover:text-white ml-1">&times;</button>
                </div>
              ))}
            </div>
          )}

          <div className="relative flex items-end gap-2">
            <div className="relative flex-1">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                placeholder="Ask about your medicines..."
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-12 py-3.5 text-sm focus:outline-none focus:ring-2 focus:ring-medic-accent resize-none h-12 max-h-32 shadow-inner"
                disabled={loading}
              />
              <label className="absolute left-3 top-3.5 text-slate-400 hover:text-medic-primary cursor-pointer transition-colors">
                <Paperclip size={20} />
                <input 
                  type="file" 
                  multiple 
                  className="hidden" 
                  onChange={handleFileSelect}
                  accept=".png,.jpg,.jpeg,.pdf"
                  disabled={loading}
                />
              </label>
            </div>
            
            <button 
              onClick={handleSend}
              disabled={loading || (!input.trim() && files.length === 0)}
              className="bg-medic-primary hover:bg-blue-600 disabled:opacity-50 text-white rounded-xl p-3.5 shadow-sm transition-colors shrink-0"
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
