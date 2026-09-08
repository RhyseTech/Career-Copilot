"use client";

import React, { useState } from 'react';

export default function ResumeJDMatchPage() {
  const [file, setFile] = useState(null);
  const [jdText, setJdText] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState("");

  const handleFileChange = (e) => {
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

      const res = await fetch("http://localhost:8000/resume-jd/match-types", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Server responded with ${res.status}`);
      }

      const data = await res.json();
      setResults(data.data.requirements);
    } catch (err) {
      console.error(err);
      setError("Failed to analyze. Make sure backend is running on port 8000.");
    } finally {
      setLoading(false);
    }
  };

  const getLabelColor = (label) => {
    switch(label) {
      case "Exact": return "bg-green-500 text-white";
      case "Related": return "bg-blue-500 text-white";
      case "Partial": return "bg-yellow-500 text-white";
      case "Transferable": return "bg-purple-500 text-white";
      case "Gap": return "bg-red-500 text-white";
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
            ) : "Analyze Match Types"}
          </button>
        </div>

        {error && (
          <div className="p-4 bg-red-900/50 border border-red-500 rounded-xl text-red-200 text-center">
            {error}
          </div>
        )}

        {results && (
          <div className="mt-12 space-y-8 animate-fade-in-up">
            
            {/* High-Level Summary Section */}
            <div className="bg-[#111111] p-8 rounded-2xl border border-gray-800 shadow-2xl">
              <div className="text-center mb-8">
                {(() => {
                  const totalReqs = results.length;
                  const satisfiedReqs = results.filter(r => ["Exact", "Related", "Partial", "Transferable"].includes(r.match.label)).length;
                  const matchScore = totalReqs > 0 ? Math.round((satisfiedReqs / totalReqs) * 100) : 0;
                  
                  return (
                    <div className="inline-block px-12 py-4 bg-gradient-to-r from-emerald-500/20 to-emerald-500/10 border border-emerald-500/50 rounded-2xl">
                      <h2 className="text-5xl font-extrabold text-emerald-400">{matchScore}% Match</h2>
                      <p className="text-emerald-500/80 mt-1 font-medium text-sm">Based on {totalReqs} extracted requirements</p>
                    </div>
                  );
                })()}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {(() => {
                  // Aggregate skills
                  const allJdSkills = new Map();
                  const matchedSkills = new Map(); // name -> { required, sentence }
                  const unmatchedSkills = new Map();

                  results.forEach(req => {
                    const isMatched = ["Exact", "Related", "Partial", "Transferable"].includes(req.match.label);
                    
                    // Use the raw extracted text as the skill name
                    const skill = req.text;
                    
                    // Add to all skills
                    if (!allJdSkills.has(skill) || req.required) {
                      allJdSkills.set(skill, { required: req.required, sentence: req.text }); // prioritize marking it required
                    }
                    
                    if (isMatched) {
                      matchedSkills.set(skill, { required: req.required, sentence: req.text });
                      unmatchedSkills.delete(skill); // If it was previously marked unmatched by another req, remove it
                    } else {
                      if (!matchedSkills.has(skill)) {
                        unmatchedSkills.set(skill, { required: req.required, sentence: req.text });
                      }
                    }
                  });

                  return (
                    <>
                      {/* All JD Skills */}
                      <div className="bg-[#0A0A0A] p-6 rounded-xl border border-gray-800 flex flex-col max-h-80">
                        <h3 className="text-lg font-bold text-gray-200 mb-4 flex items-center gap-2">
                          <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path></svg>
                          Extracted JD Skills
                        </h3>
                        <div className="flex flex-wrap gap-2 overflow-y-auto pr-2 custom-scrollbar">
                          {Array.from(allJdSkills.entries()).length === 0 ? (
                            <span className="text-gray-600 italic">No exact skills extracted.</span>
                          ) : (
                            Array.from(allJdSkills.entries()).map(([skill, data], i) => (
                              <div key={i} className="group relative">
                                <span className={`px-2.5 py-1 rounded-lg text-xs font-medium border flex items-center gap-1.5 cursor-help ${data.required ? 'bg-blue-500/10 text-blue-400 border-blue-500/30' : 'bg-gray-700/30 text-gray-300 border-gray-600/50'}`}>
                                  {skill}
                                </span>
                                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-64 p-2 bg-gray-900 text-xs text-gray-300 border border-gray-700 rounded shadow-xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
                                  <span className="font-bold text-gray-400 block mb-1">Source context:</span>
                                  "{data.sentence}"
                                </div>
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
                          {Array.from(matchedSkills.entries()).length === 0 ? (
                            <span className="text-gray-600 italic">No exact skills matched.</span>
                          ) : (
                            Array.from(matchedSkills.entries()).map(([skill, data], i) => (
                              <div key={i} className="group relative">
                                <span className={`px-2.5 py-1 rounded-lg text-xs font-medium border flex items-center gap-1.5 cursor-help ${data.required ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' : 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30'}`}>
                                  {skill}
                                  <span className={`w-1 h-1 rounded-full ${data.required ? 'bg-emerald-500' : 'bg-yellow-500'}`}></span>
                                </span>
                                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-64 p-2 bg-gray-900 text-xs text-gray-300 border border-gray-700 rounded shadow-xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
                                  <span className="font-bold text-gray-400 block mb-1">Source context:</span>
                                  "{data.sentence}"
                                </div>
                              </div>
                            ))
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
                          {Array.from(unmatchedSkills.entries()).length === 0 ? (
                            <span className="text-gray-600 italic">Great job! No key skills missing.</span>
                          ) : (
                            Array.from(unmatchedSkills.entries()).map(([skill, data], i) => (
                              <div key={i} className="group relative">
                                <span className={`px-2.5 py-1 rounded-lg text-xs font-medium border flex items-center gap-1.5 cursor-help ${data.required ? 'bg-red-500/10 text-red-400 border-red-500/30' : 'bg-gray-700/30 text-gray-400 border-gray-600/50'}`}>
                                  {skill}
                                  <span className={`w-1 h-1 rounded-full ${data.required ? 'bg-red-500' : 'bg-gray-500'}`}></span>
                                </span>
                                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-64 p-2 bg-gray-900 text-xs text-gray-300 border border-gray-700 rounded shadow-xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
                                  <span className="font-bold text-gray-400 block mb-1">Source context:</span>
                                  "{data.sentence}"
                                </div>
                              </div>
                            ))
                          )}
                        </div>
                      </div>
                    </>
                  );
                })()}
              </div>

              <div className="mt-8 flex flex-col md:flex-row gap-6">
                <div className="flex gap-4 text-xs text-gray-400 flex-1 items-center justify-center bg-[#0A0A0A] border border-gray-800 rounded-xl p-3">
                  <span className="font-semibold text-gray-300 mr-2">Color Legend:</span>
                  <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-blue-500"></span> Required (JD)</span>
                  <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-emerald-500"></span> Essential (Matched)</span>
                  <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-yellow-500"></span> Desirable (Matched)</span>
                  <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-red-500"></span> Missing Essential</span>
                </div>

                <div className="flex-1 bg-[#0A0A0A] border border-gray-800 rounded-xl p-4 text-xs text-gray-300">
                  <h4 className="font-bold text-gray-200 mb-2">Deterministic Match Rules</h4>
                  <ul className="space-y-1.5">
                    <li><span className="font-bold text-green-500 w-24 inline-block">Exact:</span> Same canonical skill or direct phrase match.</li>
                    <li><span className="font-bold text-blue-500 w-24 inline-block">Related:</span> Different words, high semantic similarity.</li>
                    <li><span className="font-bold text-yellow-500 w-24 inline-block">Partial:</span> Requirement partly covered, but missing depth or years.</li>
                    <li><span className="font-bold text-purple-500 w-24 inline-block">Transferable:</span> No direct skill, but nearby evidence from related stack.</li>
                    <li><span className="font-bold text-red-500 w-24 inline-block">Gap:</span> No credible supporting evidence.</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Detailed Line-by-Line Evidence Analysis */}
            <div className="pt-8">
              <h2 className="text-3xl font-bold border-b border-gray-800 pb-4 mb-6">Detailed Requirement Analysis</h2>
              <div className="grid gap-4">
                {results.map((req, idx) => (
                  <div key={idx} className="bg-[#111111] p-6 rounded-xl border border-gray-800 hover:border-gray-600 transition-colors group">
                    <div className="flex flex-col md:flex-row justify-between items-start gap-6">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-3">
                          <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${getLabelColor(req.match.label)}`}>
                            {req.match.label}
                          </span>
                          <span className="text-gray-500 text-sm">{req.type === 'technical_skill' ? 'Technical' : 'General'}</span>
                          {req.required ? (
                            <span className="text-red-400 text-xs border border-red-400/30 px-2 py-0.5 rounded">Required</span>
                          ) : (
                            <span className="text-green-400 text-xs border border-green-400/30 px-2 py-0.5 rounded">Preferred</span>
                          )}
                        </div>
                        <p className="text-lg text-gray-200 font-medium leading-relaxed">{req.text}</p>
                      </div>
                      
                      <div className="w-full md:w-1/3 bg-[#0A0A0A] p-5 rounded-xl border border-gray-800 shadow-inner">
                        <p className="text-xs text-gray-500 mb-2 font-bold uppercase tracking-wider">Resume Evidence</p>
                        {req.match.label === "Gap" ? (
                          <p className="text-sm text-gray-400 italic">No credible supporting evidence found in resume.</p>
                        ) : (
                          <div>
                            <p className="text-sm text-gray-300 italic mb-3">"{req.match.evidence.text_span}"</p>
                            <div className="flex items-center justify-between border-t border-gray-800 pt-3">
                              <span className="text-xs font-medium text-blue-400 bg-blue-400/10 px-2 py-1 rounded border border-blue-400/20">
                                {req.match.evidence.section}
                              </span>
                              <span className="text-xs text-gray-400 flex items-center gap-1">
                                Confidence: <span className="font-medium text-gray-300">{(req.match.similarity_scores.semantic * 100).toFixed(0)}%</span>
                              </span>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
