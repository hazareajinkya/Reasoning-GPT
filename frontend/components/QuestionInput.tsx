"use client";

import { useState } from "react";
import { sampleProblems } from "@/data/sampleProblems";

interface QuestionInputProps {
  onSolve: (question: string) => Promise<boolean>;
  loading: boolean;
}

export default function QuestionInput({ onSolve, loading }: QuestionInputProps) {
  const [question, setQuestion] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (question.trim() && !loading) {
      const questionText = question.trim();
      await onSolve(questionText);
      // Keep the question in the textarea for reference
    }
  };

  const handleSampleClick = (problem: string) => {
    setQuestion(problem);
  };

  return (
    <div className="rounded-xl border border-slate-950/40 bg-slate-900/50 backdrop-blur-sm shadow-xl shadow-slate-950/50">
      <div className="flex flex-col space-y-1.5 p-6 pb-4">
        <div className="font-semibold tracking-tight flex items-center gap-2 text-lg text-white">
          <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-blue-500/10">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4 text-blue-400">
              <path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"></path>
              <path d="M9 18h6"></path>
              <path d="M10 22h4"></path>
            </svg>
          </div>
          Enter Your DILR Problem
        </div>
      </div>
      
      <div className="p-6 pt-0 space-y-4">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="relative">
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Paste or type your CAT DILR problem here..."
              className="flex w-full rounded-md border px-3 py-2 text-base shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 md:text-sm min-h-[140px] resize-none bg-slate-800/50 border-slate-950/30 text-slate-100 placeholder:text-slate-500 focus:border-blue-500/50 focus:ring-blue-500/20 transition-all duration-200"
              disabled={loading}
            />
          </div>
          
          <div className="flex flex-col sm:flex-row gap-3 sm:items-center sm:justify-between">
            <p className="text-xs text-slate-500">
              Tip: Be specific and include all constraints from the problem
            </p>
            <button
              type="submit"
              disabled={loading || !question.trim()}
              className="inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 h-9 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-600/25 transition-all duration-200 hover:shadow-blue-500/30 disabled:shadow-none"
            >
              {loading ? (
                <>
                  <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Solving...
                </>
              ) : (
                <>
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4">
                    <path d="M14.536 21.686a.5.5 0 0 0 .937-.024l6.5-19a.496.496 0 0 0-.635-.635l-19 6.5a.5.5 0 0 0-.024.937l7.93 3.18a2 2 0 0 1 1.112 1.11z"></path>
                    <path d="m21.854 2.147-10.94 10.939"></path>
                  </svg>
                  Solve Problem
                </>
              )}
            </button>
          </div>
        </form>

        {/* Sample Problems */}
        <div className="pt-4 border-t border-slate-950/40">
          <p className="text-sm text-slate-400 mb-3 font-medium">Try a sample problem:</p>
          <div className="grid gap-2">
            {sampleProblems.map((sample) => (
              <button
                key={sample.id}
                onClick={() => handleSampleClick(sample.problem)}
                className="text-left p-3 rounded-lg bg-slate-800/30 border border-slate-950/30 text-sm text-slate-300 hover:bg-slate-800/50 hover:border-blue-500/30 hover:text-white transition-all duration-200"
              >
                <div className="font-medium text-slate-200 mb-1">{sample.title}</div>
                <div className="text-xs text-slate-400 line-clamp-2">
                  {sample.problem.length > 150 
                    ? sample.problem.substring(0, 150) + "..." 
                    : sample.problem}
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
