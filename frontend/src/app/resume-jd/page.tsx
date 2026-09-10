"use client";

import React, { useState } from 'react';
import { Phase5Dashboard } from '../../components/dashboard/Phase5Dashboard';
import { Phase5Score } from '../../types/phase5';

export default function ResumeJDMatchPage() {
  const [file, setFile] = useState<File | null>(null);
  const [jdText, setJdText] = useState("");
  const [loading, setLoading] = useState(false);
  const [analysisData, setAnalysisData] = useState<any | null>(null);
  const [error, setError] = useState("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleAnalyze = async () => {
    if (!file || !jdText.trim()) {
      setError("Please provide both a Resume file and Job Description text.");
      return;
    }
    
    setError("");
    setLoading(true);
    
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("jd_text", jdText);

      const res = await fetch("http://localhost:8000/resume-jd/analysis/run", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Server responded with ${res.status}`);
      }

      const data = await res.json();
      setAnalysisData(data);
    } catch (err: unknown) {
      console.error(err);
      setError("Failed to analyze. Make sure backend is running on port 8000.");
    } finally {
      setLoading(false);
    }
  };

  const getLabelColor = (label: string) => {
    switch(label) {
      case "EXACT": return "bg-green-500 text-white";
      case "RELATED": return "bg-blue-500 text-white";
      case "PARTIAL": return "bg-yellow-500 text-white";
      case "TRANSFERABLE": return "bg-purple-500 text-white";
      case "GAP": return "bg-red-500 text-white";
      default: return "bg-gray-500 text-white";
    }
  };

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-white p-8 font-sans">
      <div className="max-w-6xl mx-auto space-y-8">
        
        <div className="text-center space-y-4">
          <h1 className="text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600">
            Resume + JD Match Analysis
          </h1>
          <p className="text-gray-400 text-lg">
            Deterministic Pipeline matching requirements against evidence.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Upload Section */}
          <div className="bg-[#111111] p-6 rounded-2xl border border-gray-800 shadow-xl">
            <h2 className="text-2xl font-semibold mb-4 text-gray-200">1. Upload Resume</h2>
            <div className="border-2 border-dashed border-gray-700 rounded-xl p-8 text-center hover:border-blue-500 transition-colors cursor-pointer relative">
              <input 
                type="file" 
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" 
                onChange={handleFileChange}
                accept=".pdf,.docx"
              />
              <div className="space-y-2">
                <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48" aria-hidden="true">
                  <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                <div className="text-gray-300">
                  {file ? <span className="text-blue-400 font-medium">{file.name}</span> : "Click or drag file to this area"}
                </div>
                <p className="text-xs text-gray-500">PDF or DOCX up to 10MB</p>
              </div>
            </div>
          </div>

          {/* JD Section */}
          <div className="bg-[#111111] p-6 rounded-2xl border border-gray-800 shadow-xl flex flex-col">
            <h2 className="text-2xl font-semibold mb-4 text-gray-200">2. Paste Job Description</h2>
            <textarea 
              className="flex-1 w-full bg-[#0A0A0A] border border-gray-700 rounded-xl p-4 text-gray-300 focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 resize-none transition-all"
              placeholder="Paste the job requirements here..."
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
            />
          </div>
        </div>

        <div className="flex justify-center">
          <button 
            onClick={handleAnalyze}
            disabled={loading}
            className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full font-bold text-lg hover:shadow-[0_0_20px_rgba(124,58,237,0.5)] transition-all hover:-translate-y-1 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {loading ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing...
              </>
            ) : "Analyze Requirements"}
          </button>
        </div>

        {error && (
          <div className="p-4 bg-red-900/50 border border-red-500 rounded-xl text-red-200 text-center">
            {error}
          </div>
        )}

        {analysisData && analysisData.phase_5?.score && (
          <div className="mt-12 space-y-8 animate-fade-in-up">
            
            {/* Phase 5 Primary Score Dashboard */}
            <div className="pt-8">
              <h2 className="text-3xl font-bold border-b border-gray-800 pb-4 mb-6 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">Phase 5 Deterministic Match Score</h2>
              <Phase5Dashboard scoreData={analysisData.phase_5.score} />
            </div>

            {/* Three Skills Sections */}
            <div className="bg-[#111111] p-8 rounded-2xl border border-gray-800 shadow-2xl">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {(() => {
                  const jdRequirements = analysisData.phase_3?.jd_requirements || [];
                  const matchEdges = analysisData.phase_4?.match_edges || [];

                  // Map Phase 3 requirements
                  const allJdSkills = jdRequirements;
                  
                  // Map Phase 3 req_id to raw_value and type
                  const reqMap = jdRequirements.reduce((acc: any, req: any) => {
                    acc[req.requirement_id] = req;
                    return acc;
                  }, {});
                  
                  // Map Phase 4 edges for matched vs unmatched
                  const matchedSkills = matchEdges.filter((e: any) => ["EXACT", "RELATED", "PARTIAL", "TRANSFERABLE"].includes(e.match_type));
                  const unmatchedSkills = matchEdges.filter((e: any) => e.match_type === "GAP");

                  return (
                    <>
                      {/* All JD Skills */}
                      <div className="bg-[#0A0A0A] p-6 rounded-xl border border-gray-800 flex flex-col max-h-80">
                        <h3 className="text-lg font-bold text-gray-200 mb-4 flex items-center gap-2">
                          <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path></svg>
                          Extracted JD Skills
                        </h3>
                        <div className="flex flex-wrap gap-2 overflow-y-auto pr-2 custom-scrollbar">
                          {allJdSkills.length === 0 ? (
                            <span className="text-gray-600 italic">No exact skills extracted.</span>
                          ) : (
                            allJdSkills.map((req: any, i: number) => (
                              <div key={i} className="group relative">
                                <span className={`px-2.5 py-1 rounded-lg text-xs font-medium border flex items-center gap-1.5 cursor-help ${req.requirement_type === 'REQUIRED' ? 'bg-blue-500/10 text-blue-400 border-blue-500/30' : 'bg-gray-700/30 text-gray-300 border-gray-600/50'}`}>
                                  {req.raw_value}
                                </span>
                              </div>
                            ))
                          )}
                        </div>
                      </div>

                      {/* Matched Skills */}
                      <div className="bg-[#0A0A0A] p-6 rounded-xl border border-gray-800 flex flex-col max-h-80">
                        <h3 className="text-lg font-bold text-gray-200 mb-4 flex items-center gap-2">
                          <svg className="w-5 h-5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>
                          Matched Skills
                        </h3>
                        <div className="flex flex-wrap gap-2 overflow-y-auto pr-2 custom-scrollbar">
                          {matchedSkills.length === 0 ? (
                            <span className="text-gray-600 italic">No skills matched.</span>
                          ) : (
                            matchedSkills.map((edge: any, i: number) => {
                              const req = reqMap[edge.requirement_id];
                              const isReq = req?.requirement_type === 'REQUIRED';
                              const label = req?.raw_value || edge.requirement_id;
                              return (
                                <div key={i} className="group relative">
                                  <span className={`px-2.5 py-1 rounded-lg text-xs font-medium border flex items-center gap-1.5 cursor-help ${isReq ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' : 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30'}`}>
                                    {label} — {edge.match_type}
                                    <span className={`w-1 h-1 rounded-full ${isReq ? 'bg-emerald-500' : 'bg-yellow-500'}`}></span>
                                  </span>
                                </div>
                              );
                            })
                          )}
                        </div>
                      </div>

                      {/* Unmatched Skills */}
                      <div className="bg-[#0A0A0A] p-6 rounded-xl border border-gray-800 flex flex-col max-h-80">
                        <h3 className="text-lg font-bold text-gray-200 mb-4 flex items-center gap-2">
                          <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                          Unmatched Skills
                        </h3>
                        <div className="flex flex-wrap gap-2 overflow-y-auto pr-2 custom-scrollbar">
                          {unmatchedSkills.length === 0 ? (
                            <span className="text-gray-600 italic">Great job! No key skills missing.</span>
                          ) : (
                            unmatchedSkills.map((edge: any, i: number) => {
                              const req = reqMap[edge.requirement_id];
                              const isReq = req?.requirement_type === 'REQUIRED';
                              const label = req?.raw_value || edge.requirement_id;
                              return (
                                <div key={i} className="group relative">
                                  <span className={`px-2.5 py-1 rounded-lg text-xs font-medium border flex items-center gap-1.5 cursor-help ${isReq ? 'bg-red-500/10 text-red-400 border-red-500/30' : 'bg-gray-700/30 text-gray-400 border-gray-600/50'}`}>
                                    {label} — GAP
                                    <span className={`w-1 h-1 rounded-full ${isReq ? 'bg-red-500' : 'bg-gray-500'}`}></span>
                                  </span>
                                </div>
                              );
                            })
                          )}
                        </div>
                      </div>
                    </>
                  );
                })()}
              </div>
            </div>

            {/* Detailed Line-by-Line Evidence Analysis */}
            <div className="pt-8">
              <h2 className="text-3xl font-bold border-b border-gray-800 pb-4 mb-6">Detailed Requirement Analysis</h2>
              <div className="grid gap-4">
                {analysisData.phase_5.score.requirement_scores.map((req: any, idx: number) => {
                  const coverage = typeof req.coverage === "number" ? req.coverage : 0;
                  // Determine best match type from atom scores if available
                  let bestMatchType = "GAP";
                  if (req.atom_scores && req.atom_scores.length > 0) {
                     const types = req.atom_scores.map((a: any) => a.match_type);
                     if (types.includes("EXACT")) bestMatchType = "EXACT";
                     else if (types.includes("RELATED")) bestMatchType = "RELATED";
                     else if (types.includes("PARTIAL")) bestMatchType = "PARTIAL";
                     else if (types.includes("TRANSFERABLE")) bestMatchType = "TRANSFERABLE";
                  }
                  
                  return (
                    <div key={idx} className="bg-[#111111] p-6 rounded-xl border border-gray-800 hover:border-gray-600 transition-colors group">
                      <div className="flex flex-col md:flex-row justify-between items-start gap-6">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-3">
                            <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${getLabelColor(bestMatchType)}`}>
                              {bestMatchType}
                            </span>
                            {req.requirement_type === 'REQUIRED' ? (
                              <span className="text-red-400 text-xs border border-red-400/30 px-2 py-0.5 rounded">Required</span>
                            ) : (
                              <span className="text-green-400 text-xs border border-green-400/30 px-2 py-0.5 rounded">Preferred</span>
                            )}
                          </div>
                          <p className="text-lg text-gray-200 font-medium leading-relaxed">{req.requirement_text}</p>
                          <p className="text-sm text-gray-500 mt-2">
                            Coverage: {(coverage * 100).toFixed(0)}% | Contribution: {(req.requirement_score || 0).toFixed(2)}
                          </p>
                        </div>
                        
                        <div className="w-full md:w-1/3 bg-[#0A0A0A] p-5 rounded-xl border border-gray-800 shadow-inner">
                          <p className="text-xs text-gray-500 mb-2 font-bold uppercase tracking-wider">Phase 5 Explanation</p>
                          <div>
                            <p className="text-sm text-gray-300 italic mb-3">"{req.deterministic_explanation || "No explanation provided."}"</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
