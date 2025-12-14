"use client";

interface HistoryPanelProps {
  history: Array<{
    id: number;
    question: string;
    solution: any;
    timestamp: string;
  }>;
  onSelect: (item: any) => void;
  onClear?: () => void;
  isOpen?: boolean;
  onClose?: () => void;
}

export default function HistoryPanel({ history, onSelect, onClear, isOpen = false, onClose }: HistoryPanelProps) {
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    if (diffDays === 1) return "1d ago";
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <aside
      className={`
        fixed lg:sticky top-0 left-0 z-50 lg:z-0
        h-screen w-80 lg:w-72 xl:w-80
        bg-slate-900/95 lg:bg-transparent backdrop-blur-xl lg:backdrop-blur-none
        border-r border-slate-950/40
        transform transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}
    >
      <div className="flex flex-col h-full pt-4 lg:pt-20">
        {/* Header */}
        <div className="flex items-center justify-between px-4 mb-4">
          <div className="flex items-center gap-2">
            <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-slate-800/50">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4 text-slate-400">
                <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"></path>
                <path d="M3 3v5h5"></path>
                <path d="M12 7v5l4 2"></path>
              </svg>
            </div>
            <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
              History
            </h2>
          </div>
          <div className="flex items-center gap-2">
            {onClear && (
              <button
                onClick={() => {
                  if (confirm("Clear all history?")) {
                    onClear();
                  }
                }}
                className="inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 h-8 w-8 text-slate-500 hover:text-red-400 hover:bg-red-500/10"
                title="Clear history"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4">
                  <path d="M3 6h18"></path>
                  <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path>
                  <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path>
                  <line x1="10" x2="10" y1="11" y2="17"></line>
                  <line x1="14" x2="14" y1="11" y2="17"></line>
                </svg>
              </button>
            )}
            <button
              onClick={onClose}
              className="inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 h-8 w-8 text-slate-500 hover:text-white hover:bg-accent lg:hidden"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4">
                <path d="M18 6 6 18"></path>
                <path d="m6 6 12 12"></path>
              </svg>
            </button>
          </div>
        </div>

        {/* History List */}
        <div className="flex-1 px-2 overflow-y-auto">
          <div className="space-y-2 pb-4">
            {history.length === 0 ? (
              <p className="text-sm text-slate-500 text-center py-8 px-4">
                No questions solved yet. Your history will appear here.
              </p>
            ) : (
              history.map((item) => (
                <button
                  key={item.id}
                  onClick={() => {
                    onSelect(item);
                    if (onClose) onClose();
                  }}
                  className="w-full p-3 rounded-xl bg-slate-800/30 border border-slate-950/30 hover:bg-slate-800/50 hover:border-blue-500/30 transition-all duration-200 text-left group"
                >
                  <div className="flex items-start gap-2">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4 text-emerald-500 mt-0.5 flex-shrink-0">
                      <path d="M21.801 10A10 10 0 1 1 17 3.335"></path>
                      <path d="m9 11 3 3L22 4"></path>
                    </svg>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-slate-300 line-clamp-2 group-hover:text-white transition-colors">
                        {item.question}
                      </p>
                      <p className="text-xs text-slate-500 mt-1.5">
                        {formatTime(item.timestamp)}
                      </p>
                    </div>
                  </div>
                </button>
              ))
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-950/40">
          <p className="text-xs text-slate-600 text-center">
            {history.length} problem{history.length !== 1 ? 's' : ''} solved
          </p>
        </div>
      </div>
    </aside>
  );
}
