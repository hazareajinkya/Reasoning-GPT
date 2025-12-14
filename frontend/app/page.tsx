"use client";

import { useState } from "react";
import QuestionInput from "@/components/QuestionInput";
import SolutionDisplay from "@/components/SolutionDisplay";
import HistoryPanel from "@/components/HistoryPanel";

export default function Home() {
  const [solution, setSolution] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleSolve = async (question: string): Promise<boolean> => {
    setLoading(true);
    setError(null);
    setSolution(null);

    try {
      // Get backend URL from environment variable or use localhost for development
      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      
      // Log for debugging (remove in production if needed)
      if (!process.env.NEXT_PUBLIC_API_URL) {
        console.warn("NEXT_PUBLIC_API_URL not set, using localhost. Set this in Vercel environment variables!");
      }
      
      // Test backend connectivity first
      try {
        const healthCheck = await fetch(`${API_URL}/health`, { method: "GET" });
        if (!healthCheck.ok) {
          throw new Error(`Backend health check failed: ${healthCheck.status}`);
        }
      } catch (healthErr: any) {
        throw new Error(`Cannot connect to backend: ${healthErr.message}. Make sure backend is running on ${API_URL}`);
      }
      
      // Create abort controller for timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 240000); // 4 minute timeout
      
      const response = await fetch(`${API_URL}/solve`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question,
          top_k: 4,
        }),
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);

      if (!response.ok) {
        let errorMessage = "Failed to solve question";
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch {
          errorMessage = `Server error: ${response.status} ${response.statusText}`;
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();
      
      // Validate response structure
      if (!data || typeof data !== 'object') {
        throw new Error("Invalid response from server");
      }

      const validatedSolution = {
        direct: data.direct || "No direct answer available.",
        step_by_step: data.step_by_step || "No step-by-step solution available.",
        intuitive: data.intuitive || "No intuitive explanation available.",
        shortcut: data.shortcut || "No shortcut method available.",
        retrieved_ids: data.retrieved_ids || [],
      };

      setSolution(validatedSolution);
      
      // Add to history
      const historyItem = {
        id: Date.now(),
        question,
        solution: validatedSolution,
        timestamp: new Date().toISOString(),
      };
      setHistory((prev) => [historyItem, ...prev].slice(0, 50));
      
      return true;
    } catch (err: any) {
      console.error("Error solving question:", err);
      
      let errorMessage = "An error occurred.";
      if (err.name === "AbortError" || err.name === "TimeoutError") {
        errorMessage = "Request timed out. The backend might be slow or unresponsive.";
      } else if (err.message?.includes("Failed to fetch") || err.message?.includes("NetworkError")) {
        const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        errorMessage = `Cannot connect to backend. Make sure the backend is running on ${API_URL}`;
      } else if (err.message) {
        errorMessage = err.message;
      } else {
        errorMessage = "An error occurred. Please check if the backend is running.";
      }
      
      setError(errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const handleHistorySelect = (item: any) => {
    setSolution(item.solution);
  };

  return (
    <div className="app-container min-h-screen bg-slate-950">
      {/* Background gradient blurs */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl"></div>
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-blue-600/5 rounded-full blur-3xl"></div>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-slate-900/50 rounded-full blur-3xl"></div>
      </div>

      <div className="relative flex">
        {/* Sidebar */}
        <HistoryPanel
          history={history}
          onSelect={handleHistorySelect}
          onClear={() => setHistory([])}
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
        />

        {/* Main Content */}
        <div className="flex-1 flex flex-col min-h-screen">
          {/* Header */}
          <header className="sticky top-0 z-50 w-full border-b border-slate-950/40 bg-slate-950/80 backdrop-blur-xl">
            <div className="flex h-16 items-center justify-between px-4 md:px-6 lg:px-8">
              <button
                onClick={() => setSidebarOpen(true)}
                className="inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 h-9 w-9 lg:hidden text-slate-400 hover:text-white hover:bg-slate-800/50"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-5 w-5">
                  <path d="M4 12h16"></path>
                  <path d="M4 18h16"></path>
                  <path d="M4 6h16"></path>
                </svg>
              </button>
              
              <div className="flex items-center gap-3">
                <div className="relative">
                  <div className="absolute inset-0 bg-blue-500/20 blur-xl rounded-full"></div>
                  <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 shadow-lg shadow-blue-500/25">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-5 w-5 text-white">
                      <path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"></path>
                      <path d="M20 3v4"></path>
                      <path d="M22 5h-4"></path>
                      <path d="M4 17v2"></path>
                      <path d="M5 18H3"></path>
                    </svg>
                  </div>
                </div>
                <div className="flex flex-col">
                  <h1 className="text-xl md:text-2xl font-bold bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                    Reasoning GPT
                  </h1>
                  <p className="hidden sm:block text-xs md:text-sm text-slate-400 font-medium">
                    Learn how to develop easy approach to any CAT DILR problem
                  </p>
                </div>
              </div>
              
              <div className="w-10 lg:w-auto"></div>
            </div>
          </header>

          {/* Main Content Area */}
          <main className="flex-1 px-4 md:px-6 lg:px-8 py-8">
            <div className="max-w-4xl mx-auto space-y-8">
              <QuestionInput 
                onSolve={handleSolve}
                loading={loading}
              />
              
              {error && (
                <div className="rounded-xl border border-red-800/50 bg-red-900/20 backdrop-blur-sm shadow-xl p-6">
                  <p className="text-red-200 text-sm">{error}</p>
                </div>
              )}

              {solution ? (
                <SolutionDisplay solution={solution} />
              ) : (
                <div className="rounded-xl border border-slate-950/40 bg-slate-900/50 backdrop-blur-sm shadow-xl shadow-slate-950/50">
                  <div className="p-6 flex flex-col items-center justify-center py-16 px-4">
                    <div className="w-16 h-16 rounded-2xl bg-slate-800/50 flex items-center justify-center mb-4">
                      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-8 w-8 text-slate-600">
                        <path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"></path>
                        <path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z"></path>
                        <path d="M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4"></path>
                        <path d="M17.599 6.5a3 3 0 0 0 .399-1.375"></path>
                        <path d="M6.003 5.125A3 3 0 0 0 6.401 6.5"></path>
                        <path d="M3.477 10.896a4 4 0 0 1 .585-.396"></path>
                        <path d="M19.938 10.5a4 4 0 0 1 .585.396"></path>
                        <path d="M6 18a4 4 0 0 1-1.967-.516"></path>
                        <path d="M19.967 17.484A4 4 0 0 1 18 18"></path>
                      </svg>
                    </div>
                    <h3 className="text-lg font-medium text-slate-400 mb-2">No Solution Yet</h3>
                    <p className="text-sm text-slate-500 text-center max-w-md">
                      Enter a CAT DILR problem above and click "Solve Problem" to see detailed solutions with multiple approaches.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </main>

          {/* Footer */}
          <footer className="border-t border-slate-950/40 py-6 px-4">
            <p className="text-center text-sm text-slate-600">
              Reasoning GPT — Master CAT DILR with AI-powered solutions
            </p>
          </footer>
        </div>
      </div>
    </div>
  );
}
