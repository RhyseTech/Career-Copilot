'use client';

import React, { createContext, useContext, useState, ReactNode } from 'react';
import { ParsedResume, ATSScoreResult, SuggestAllResult, DiagnoseResult } from './api';

interface ResumeContextType {
  // Upload Data
  resumeId: string | null;
  filename: string | null;
  rawText: string | null;
  structuredResume: Record<string, unknown> | null;
  jdText: string | null;

  // Analysis Data
  atsScore: ATSScoreResult | null;
  diagnostics: DiagnoseResult | null;
  
  // Optimization Data
  suggestions: SuggestAllResult | null;

  // Setters
  setUploadData: (data: {
    resumeId: string;
    filename: string;
    rawText: string;
    structuredResume: Record<string, unknown>;
    jdText?: string;
  }) => void;
  setAtsData: (score: ATSScoreResult, diagnostics?: DiagnoseResult) => void;
  setOptimizationData: (data: SuggestAllResult) => void;
  updateRawText: (newText: string) => void;
  updateStructuredResume: (newJson: Record<string, unknown>) => void;
  
  // Reset
  clearSession: () => void;
}

const ResumeContext = createContext<ResumeContextType | undefined>(undefined);

export function ResumeProvider({ children }: { children: ReactNode }) {
  const [resumeId, setResumeId] = useState<string | null>(null);
  const [filename, setFilename] = useState<string | null>(null);
  const [rawText, setRawText] = useState<string | null>(null);
  const [structuredResume, setStructuredResume] = useState<Record<string, unknown> | null>(null);
  const [jdText, setJdText] = useState<string | null>(null);

  const [atsScore, setAtsScore] = useState<ATSScoreResult | null>(null);
  const [diagnostics, setDiagnostics] = useState<DiagnoseResult | null>(null);
  
  const [suggestions, setSuggestions] = useState<SuggestAllResult | null>(null);

  const setUploadData = (data: {
    resumeId: string;
    filename: string;
    rawText: string;
    structuredResume: Record<string, unknown>;
    jdText?: string;
  }) => {
    setResumeId(data.resumeId);
    setFilename(data.filename);
    setRawText(data.rawText);
    setStructuredResume(data.structuredResume);
    if (data.jdText) setJdText(data.jdText);
  };

  const setAtsData = (score: ATSScoreResult, diags?: DiagnoseResult) => {
    setAtsScore(score);
    if (diags) setDiagnostics(diags);
  };

  const setOptimizationData = (data: SuggestAllResult) => {
    setSuggestions(data);
  };

  const updateRawText = (newText: string) => {
    setRawText(newText);
  };

  const updateStructuredResume = (newJson: Record<string, unknown>) => {
    setStructuredResume(newJson);
  };

  const clearSession = () => {
    setResumeId(null);
    setFilename(null);
    setRawText(null);
    setStructuredResume(null);
    setJdText(null);
    setAtsScore(null);
    setDiagnostics(null);
    setSuggestions(null);
  };

  return (
    <ResumeContext.Provider
      value={{
        resumeId,
        filename,
        rawText,
        structuredResume,
        jdText,
        atsScore,
        diagnostics,
        suggestions,
        setUploadData,
        setAtsData,
        setOptimizationData,
        updateRawText,
        updateStructuredResume,
        clearSession,
      }}
    >
      {children}
    </ResumeContext.Provider>
  );
}

export function useResumeStore() {
  const context = useContext(ResumeContext);
  if (context === undefined) {
    throw new Error('useResumeStore must be used within a ResumeProvider');
  }
  return context;
}
