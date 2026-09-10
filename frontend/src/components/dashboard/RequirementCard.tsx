import React, { useState } from 'react';
import { RequirementScore } from '../../types/phase5';
import { ChevronDown, ChevronUp } from 'lucide-react';

interface RequirementCardProps {
  score: RequirementScore;
}

export const RequirementCard: React.FC<RequirementCardProps> = ({ score }) => {
  const [expanded, setExpanded] = useState(false);

  // Determine the overall label to display based on the highest atom coverage, or explicitly check atoms
  // Phase 5 doesn't have a single "label" for the requirement, it has `coverage` and individual `atom_scores`.
  // The UI spec asks for a classification badge (EXACT, PARTIAL, GAP, etc.) per requirement.
  // We can derive a primary label from the coverage or the atom match types.
  const getPrimaryLabel = () => {
    if (score.coverage === 1.0) return "EXACT";
    if (score.coverage === 0.0) return "GAP";
    
    // Check if we have transferable
    const hasTransferable = score.atom_scores.some(a => a.match_type === 'TRANSFERABLE');
    if (hasTransferable) return "TRANSFERABLE";
    
    const hasRelated = score.atom_scores.some(a => a.match_type === 'RELATED');
    if (hasRelated && score.coverage >= 0.75) return "RELATED";
    
    return "PARTIAL";
  };

  const label = getPrimaryLabel();

  const getLabelColor = (l: string) => {
    switch(l) {
      case "EXACT": return "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";
      case "RELATED": return "bg-blue-500/10 text-blue-400 border-blue-500/30";
      case "PARTIAL": return "bg-yellow-500/10 text-yellow-400 border-yellow-500/30";
      case "TRANSFERABLE": return "bg-purple-500/10 text-purple-400 border-purple-500/30";
      case "GAP": return "bg-red-500/10 text-red-400 border-red-500/30";
      default: return "bg-gray-500/10 text-gray-400 border-gray-500/30";
    }
  };

  const getStatusIcon = (l: string) => {
    switch(l) {
      case "EXACT": return <span className="text-emerald-400 font-bold">✓</span>;
      case "RELATED": return <span className="text-blue-400 font-bold">~</span>;
      case "PARTIAL": 
      case "TRANSFERABLE": return <span className="text-yellow-400 font-bold">△</span>;
      case "GAP": return <span className="text-red-400 font-bold">✗</span>;
      default: return null;
    }
  };

  return (
    <div className="bg-[#111111] rounded-xl border border-gray-800 overflow-hidden transition-all hover:border-gray-700">
      <div 
        className="p-4 flex items-center justify-between cursor-pointer select-none"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-4 flex-1">
          <div className="w-6 text-center text-xl">{getStatusIcon(label)}</div>
          
          <div className="flex-1">
            <h4 className="text-lg text-gray-200 font-medium">{score.requirement_text}</h4>
            <div className="flex items-center gap-2 mt-1">
              <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded border ${score.requirement_type === 'REQUIRED' ? 'text-blue-400 border-blue-400/30 bg-blue-400/10' : 'text-gray-400 border-gray-400/30 bg-gray-400/10'}`}>
                {score.requirement_type}
              </span>
              {score.is_hard_constraint && (
                <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded border text-red-400 border-red-400/30 bg-red-400/10">
                  HARD CONSTRAINT
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-6">
          <div className="flex flex-col items-end">
            <span className={`text-xs font-bold uppercase px-2.5 py-1 rounded-full border ${getLabelColor(label)}`}>
              {label}
            </span>
            <span className="text-sm font-mono text-gray-400 mt-1">
              {(score.coverage * 100).toFixed(0)}%
            </span>
          </div>
          <button className="text-gray-500 hover:text-white transition-colors p-2">
            {expanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </button>
        </div>
      </div>

      {/* Expanded Detail View */}
      {expanded && (
        <div className="border-t border-gray-800 bg-[#0A0A0A] p-6 text-sm">
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Left Column: Atoms */}
            <div>
              <h5 className="font-semibold text-gray-300 mb-3 uppercase tracking-wider text-xs">Atom Breakdown</h5>
              <div className="space-y-3">
                {score.atom_scores.map(atom => (
                  <div key={atom.atom_id} className="bg-[#111111] p-3 rounded-lg border border-gray-800">
                    <div className="flex justify-between items-start mb-1">
                      <span className="font-medium text-gray-200">{atom.atom_text}</span>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${getLabelColor(atom.match_type)}`}>
                        {atom.match_type} ({(atom.contribution * 100).toFixed(0)}%)
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Right Column: Reasoning & Traces */}
            <div className="space-y-6">
              <div>
                <h5 className="font-semibold text-gray-300 mb-2 uppercase tracking-wider text-xs">Deterministic Explanation</h5>
                <div className="bg-[#111111] p-3 rounded-lg border border-gray-800 whitespace-pre-wrap text-gray-400 font-mono text-xs leading-relaxed">
                  {score.deterministic_explanation}
                </div>
              </div>

              {score.qualifier_evaluations.length > 0 && (
                <div>
                  <h5 className="font-semibold text-gray-300 mb-2 uppercase tracking-wider text-xs">Qualifier Results</h5>
                  <div className="space-y-2">
                    {score.qualifier_evaluations.map((q, idx) => (
                      <div key={idx} className="flex justify-between items-center bg-[#111111] p-2 rounded border border-gray-800">
                        <span className="text-gray-300">{q.qualifier_type}</span>
                        {q.passed ? (
                          <span className="text-emerald-400 text-xs font-bold">SATISFIED</span>
                        ) : (
                          <span className="text-red-400 text-xs font-bold">FAILED</span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Advanced Details Details (Tertiary) */}
          <div className="mt-6 pt-4 border-t border-gray-800">
            <details className="group">
              <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-300 font-mono">
                View Advanced Traceability IDs
              </summary>
              <div className="mt-3 grid grid-cols-2 gap-4 text-[10px] font-mono text-gray-500 bg-[#111111] p-3 rounded border border-gray-800">
                <div>
                  <strong className="block text-gray-400 mb-1">Evidence IDs:</strong>
                  {score.contributing_evidence_ids.length > 0 ? (
                    <ul className="list-disc pl-4 space-y-0.5">
                      {score.contributing_evidence_ids.map(id => <li key={id} className="break-all">{id}</li>)}
                    </ul>
                  ) : <span>None</span>}
                </div>
                <div>
                  <strong className="block text-gray-400 mb-1">MatchEdge IDs:</strong>
                  {score.contributing_match_edge_ids.length > 0 ? (
                    <ul className="list-disc pl-4 space-y-0.5">
                      {score.contributing_match_edge_ids.map(id => <li key={id} className="break-all">{id}</li>)}
                    </ul>
                  ) : <span>None</span>}
                </div>
              </div>
            </details>
          </div>
          
        </div>
      )}
    </div>
  );
};
