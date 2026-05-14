import React from 'react';
import { Pill, Activity, ShieldAlert, ShieldCheck, AlertTriangle } from 'lucide-react';

export default function Sidebar({ memory }) {
  if (!memory) return null;

  const { medications = [], conditions = [], allergies = [], interactions = [] } = memory;

  const getSeverity = (text) => {
    const lower = text.toLowerCase();
    if (lower.includes('severe') || lower.includes('contraindicated') || lower.includes('hypotensive')) return { color: 'bg-medic-severe', label: 'Severe' };
    if (lower.includes('moderate')) return { color: 'bg-medic-moderate', label: 'Moderate' };
    return { color: 'bg-medic-safe', label: 'Safe' };
  };

  return (
    <div className="w-80 bg-white border-l border-medic-border h-full flex flex-col hidden lg:flex shrink-0">
      <div className="p-4 border-b border-medic-border">
        <h3 className="text-xs font-bold text-medic-accent uppercase tracking-wider mb-3">Medications on File</h3>
        <div className="flex flex-wrap gap-2">
          {medications.length === 0 ? (
            <p className="text-sm text-slate-500">No medications added yet.</p>
          ) : (
            medications.map((m, i) => (
              <div key={i} className="flex items-center gap-1.5 px-3 py-1.5 bg-medic-chatbg text-medic-primary text-sm font-medium rounded-full border border-medic-border">
                <Pill size={14} />
                <span>{m.name || m}</span>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="p-4 border-b border-medic-border flex-1 overflow-y-auto">
        <h3 className="text-xs font-bold text-medic-accent uppercase tracking-wider mb-3">Interaction Summary</h3>
        <div className="flex flex-col gap-3">
          {interactions.length === 0 ? (
             <p className="text-sm text-slate-500 leading-relaxed">
               No interactions detected with your current medications.
             </p>
          ) : (
            interactions.map((interaction, i) => {
              const isAI = interaction.includes('[AI-ESTIMATED]');
              const cleanText = interaction.replace('[AI-ESTIMATED]', '').trim();
              const [drugs, desc] = cleanText.split(':');
              const severity = getSeverity(cleanText);

              return (
                <div key={i} className="flex items-start justify-between gap-3 p-3 bg-slate-50 rounded-lg border border-slate-100">
                  <div className="flex items-start gap-2">
                    <div className={`w-2 h-2 rounded-full mt-1.5 shrink-0 ${severity.color}`} />
                    <div className="flex flex-col">
                      <span className="text-sm font-bold text-slate-800">{drugs || cleanText}</span>
                      {desc && <span className="text-xs text-slate-500 mt-0.5 leading-relaxed line-clamp-2">{desc.trim()}</span>}
                      {isAI && <span className="text-[10px] uppercase text-medic-accent font-bold mt-1 tracking-wider">AI Estimated</span>}
                    </div>
                  </div>
                  <span className={`text-xs font-bold ${severity.color.replace('bg-', 'text-')} shrink-0`}>{severity.label}</span>
                </div>
              );
            })
          )}
        </div>
      </div>

      <div className="p-4 bg-slate-50 border-t border-medic-border mt-auto">
        <p className="text-xs text-slate-500 text-center leading-relaxed">
          AI-estimated results are labelled separately and must be verified with a pharmacist.
        </p>
      </div>
    </div>
  );
}
