"use client";

import { useState } from "react";

interface SolutionDisplayProps {
  solution: {
    direct: string;
    step_by_step: string;
    intuitive: string;
    shortcut: string;
    retrieved_ids?: string[];
  };
}

export default function SolutionDisplay({ solution }: SolutionDisplayProps) {
  const [activeTab, setActiveTab] = useState<"direct" | "step_by_step" | "intuitive" | "shortcut">("direct");

  const tabs = [
    { 
      id: "direct" as const, 
      label: "Direct Answer", 
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4">
          <circle cx="12" cy="12" r="10"></circle>
          <circle cx="12" cy="12" r="6"></circle>
          <circle cx="12" cy="12" r="2"></circle>
        </svg>
      )
    },
    { 
      id: "step_by_step" as const, 
      label: "Step-by-Step", 
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4">
          <path d="M4 6h16"></path>
          <path d="M4 12h16"></path>
          <path d="M4 18h16"></path>
        </svg>
      )
    },
    { 
      id: "intuitive" as const, 
      label: "Intuitive", 
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4">
          <path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"></path>
          <path d="M9 18h6"></path>
          <path d="M10 22h4"></path>
        </svg>
      )
    },
    { 
      id: "shortcut" as const, 
      label: "Shortcut", 
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4">
          <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
        </svg>
      )
    },
  ];

  // Extract table arrays from stringified formats like "table: ['...', '...']"
  const extractTableArrays = (text: string): { cleanedText: string; extractedTables: string[][] } => {
    const extractedTables: string[][] = [];
    let cleanedText = text;
    
    // Pattern to match: table: ['line1', 'line2', ...] or ping_table: ['...'] 
    // Handles both single-line and multi-line array formats (non-greedy with s flag for newlines)
    const arrayPattern = /(\w+_?table|table):\s*\[([^\]]*)\]/gs;
    
    // Extract labeled tables (table: [...], ping_table: [...])
    const matches: Array<{ match: string; arrayContent: string; index: number }> = [];
    let match;
    
    while ((match = arrayPattern.exec(text)) !== null) {
      const arrayContent = match[2];
      
      // Parse the array content - extract string values (handles both ' and " quotes)
      const stringPattern = /'([^']*)'|"([^"]*)"/g;
      const tableLines: string[] = [];
      let stringMatch;
      
      while ((stringMatch = stringPattern.exec(arrayContent)) !== null) {
        const value = stringMatch[1] || stringMatch[2];
        if (value && value.trim().length > 0) {
          tableLines.push(value);
        }
      }
      
      if (tableLines.length > 0) {
        matches.push({
          match: match[0],
          arrayContent: arrayContent,
          index: extractedTables.length
        });
        extractedTables.push(tableLines);
      }
    }
    
    // Replace matches in reverse order to preserve indices
    for (let i = matches.length - 1; i >= 0; i--) {
      const m = matches[i];
      cleanedText = cleanedText.replace(m.match, `\n__EXTRACTED_TABLE_${m.index}__\n`);
    }
    
    // Also check for standalone arrays that look like tables (on single lines)
    const lines = cleanedText.split('\n');
    const newLines: string[] = [];
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      // Check if line contains a standalone array pattern
      const standaloneMatch = line.match(/\[([^\]]*)\]/);
      if (standaloneMatch && !line.includes('__EXTRACTED_TABLE_')) {
        const arrayContent = standaloneMatch[1];
        // Check if it looks like a table array (has multiple quoted strings)
        const quoteCount = (arrayContent.match(/'|"/g) || []).length;
        if (quoteCount >= 2) {
          const stringPattern = /'([^']*)'|"([^"]*)"/g;
          const tableLines: string[] = [];
          let stringMatch;
          
          while ((stringMatch = stringPattern.exec(arrayContent)) !== null) {
            const value = stringMatch[1] || stringMatch[2];
            if (value && (value.includes('|') || value.includes('+') || value.includes('-'))) {
              tableLines.push(value);
            }
          }
          
          if (tableLines.length > 0) {
            extractedTables.push(tableLines);
            const placeholder = `__EXTRACTED_TABLE_${extractedTables.length - 1}__`;
            // Replace the array in the line
            newLines.push(line.replace(standaloneMatch[0], placeholder));
            continue;
          }
        }
      }
      newLines.push(line);
    }
    
    return { cleanedText: newLines.join('\n'), extractedTables };
  };

  // Parse ASCII table and convert to HTML table
  const parseAsciiTable = (tableLines: string[]): JSX.Element | null => {
    if (tableLines.length < 2) return null;

    // Find separator lines (lines with + and -)
    const separatorPattern = /^[\s]*\+[\s\-+]*\+/;
    const dataPattern = /^[\s]*\|.*\|[\s]*$/;
    
    const rows: string[][] = [];
    let headers: string[] = [];
    let foundFirstDataRow = false;

    for (const line of tableLines) {
      // Skip separator lines
      if (separatorPattern.test(line)) {
        continue;
      }

      // Parse data rows (lines with | at start and end)
      if (dataPattern.test(line)) {
        // Split by | and clean up
        const parts = line.split('|');
        // Remove first and last empty parts (from leading/trailing |)
        const cells = parts
          .slice(1, -1)
          .map(cell => cell.trim().replace(/\s+/g, ' ')); // Normalize whitespace

        if (cells.length > 0 && cells.some(cell => cell.length > 0)) {
          if (!foundFirstDataRow) {
            headers = cells;
            foundFirstDataRow = true;
          } else {
            rows.push(cells);
          }
        }
      }
    }

    // If we have headers or rows, render as HTML table
    if (headers.length > 0 || rows.length > 0) {
      const maxCols = Math.max(
        headers.length,
        ...rows.map(row => row.length),
        1 // At least 1 column
      );

      return (
        <div key={`table-${Date.now()}`} className="my-4 w-full overflow-x-auto">
          <table className="w-full border-collapse border border-slate-950/30 bg-slate-800/50 rounded-lg shadow-lg">
            {headers.length > 0 && (
              <thead>
                <tr>
                  {headers.map((header, idx) => (
                    <th
                      key={idx}
                      className="border border-slate-950/30 px-4 py-3 text-left text-slate-100 font-semibold bg-slate-800/70 text-sm"
                    >
                      {header || '\u00A0'}
                    </th>
                  ))}
                  {/* Fill empty header cells if needed */}
                  {Array.from({ length: Math.max(0, maxCols - headers.length) }).map((_, idx) => (
                    <th
                      key={`empty-header-${idx}`}
                      className="border border-slate-950/30 px-4 py-3 text-left text-slate-100 font-semibold bg-slate-800/70"
                    ></th>
                  ))}
                </tr>
              </thead>
            )}
            <tbody>
              {rows.length > 0 ? (
                rows.map((row, rowIdx) => (
                  <tr key={rowIdx} className={rowIdx % 2 === 0 ? "bg-slate-800/30" : "bg-slate-800/50"}>
                    {row.map((cell, cellIdx) => (
                      <td
                        key={cellIdx}
                        className="border border-slate-950/30 px-4 py-2 text-slate-200 text-sm"
                      >
                        {cell || '\u00A0'}
                      </td>
                    ))}
                    {/* Fill empty cells if needed */}
                    {Array.from({ length: Math.max(0, maxCols - row.length) }).map((_, idx) => (
                      <td
                        key={`empty-${idx}`}
                        className="border border-slate-950/30 px-4 py-2 text-slate-200"
                      >
                        {'\u00A0'}
                      </td>
                    ))}
                  </tr>
                ))
              ) : (
                // If no data rows but we have headers, show empty row
                <tr>
                  {Array.from({ length: maxCols }).map((_, idx) => (
                    <td
                      key={idx}
                      className="border border-slate-950/30 px-4 py-2 text-slate-400 text-sm"
                    >
                      {'\u00A0'}
                    </td>
                  ))}
                </tr>
              )}
            </tbody>
          </table>
        </div>
      );
    }

    return null;
  };

  const formatText = (text: string | undefined | null) => {
    if (!text) {
      return <p className="text-slate-400 italic">No explanation available.</p>;
    }

    // Handle if text is an array (shouldn't happen, but just in case)
    if (Array.isArray(text)) {
      text = text.join("\n");
    }

    // Convert to string if not already
    let textStr = String(text);
    
    // Fix escaped newlines and other escape sequences
    textStr = textStr
      .replace(/\\n/g, '\n')  // Replace \n with actual newlines
      .replace(/\\t/g, '\t')   // Replace \t with actual tabs
      .replace(/\\r/g, '\r')   // Replace \r with actual carriage returns
      .replace(/\\\\/g, '\\'); // Replace \\ with single \

    // Try to parse if it looks like JSON
    try {
      const parsed = JSON.parse(textStr);
      if (typeof parsed === 'object' && parsed !== null) {
        // Convert object to formatted string
        if (parsed.step_by_step && typeof parsed.step_by_step === 'object') {
          // Handle nested step_by_step object
          textStr = Object.entries(parsed.step_by_step)
            .map(([key, value]) => `${key}: ${value}`)
            .join('\n\n');
        } else {
          // General object formatting
          textStr = Object.entries(parsed)
            .map(([key, value]) => {
              if (typeof value === 'object' && value !== null) {
                return `${key}:\n${JSON.stringify(value, null, 2)}`;
              }
              return `${key}: ${value}`;
            })
            .join('\n\n');
        }
      }
    } catch {
      // Not JSON, use as-is
    }

    // Extract table arrays from stringified formats
    const { cleanedText, extractedTables } = extractTableArrays(textStr);
    textStr = cleanedText;

    // Split by newlines - preserve empty lines for table formatting
    const lines = textStr.split("\n");
    
    if (lines.length === 0) {
      return <p className="text-slate-400 italic">No explanation available.</p>;
    }

    // Group consecutive table lines together and convert to HTML tables
    const elements: JSX.Element[] = [];
    let tableLines: string[] = [];
    let lineIdx = 0;

    const flushTable = () => {
      if (tableLines.length > 0) {
        const htmlTable = parseAsciiTable(tableLines);
        if (htmlTable) {
          // Add spacing before and after table
          elements.push(
            <div key={`table-wrapper-${lineIdx}`} className="my-6">
              {htmlTable}
            </div>
          );
        } else {
          // Fallback: render as pre-formatted text if parsing fails, but use word-wrap instead of horizontal scroll
          const tableContent = tableLines.join('\n');
          elements.push(
            <div key={`table-fallback-${lineIdx}`} className="my-6 w-full">
              <div className="bg-slate-800/50 rounded p-3 border border-slate-950/30">
                <pre className="font-mono text-xs sm:text-sm text-slate-200 whitespace-pre-wrap break-all">
                  {tableContent}
                </pre>
              </div>
            </div>
          );
        }
        tableLines = [];
        lineIdx++;
      }
    };

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      
      // Check if this is a placeholder for an extracted table
      const tableMatch = line.match(/__EXTRACTED_TABLE_(\d+)__/);
      if (tableMatch) {
        flushTable(); // Flush any pending table lines
        const tableIndex = parseInt(tableMatch[1]);
        if (extractedTables[tableIndex]) {
          const htmlTable = parseAsciiTable(extractedTables[tableIndex]);
          if (htmlTable) {
            elements.push(htmlTable);
          } else {
            // If parsing fails, still try to render as table
            const tableContent = extractedTables[tableIndex].join('\n');
            const fallbackTable = parseAsciiTable(extractedTables[tableIndex]);
            if (fallbackTable) {
              elements.push(fallbackTable);
            } else {
              // Last resort: render as text but without horizontal scroll
              elements.push(
                <div key={`table-extracted-${tableIndex}`} className="my-4 w-full">
                  <div className="bg-slate-800/50 rounded p-3 border border-slate-950/30">
                    <pre className="font-mono text-xs sm:text-sm text-slate-200 whitespace-pre-wrap break-all">
                      {tableContent}
                    </pre>
                  </div>
                </div>
              );
            }
          }
        }
        continue;
      }
      
      // Check if this is a table line - be more strict to avoid grouping explanations with tables
      const isTableLine = (
        (line.includes('|') && (line.includes('+---') || line.includes('----') || line.match(/^\s*\|.*\|/))) ||
        (line.trim().startsWith('+') && (line.includes('---') || line.includes('==='))) ||
        (line.includes('|') && line.includes('-') && line.match(/^[\s]*\+[\s\-+]*\+/))
      );
      
      // Also check if line starts with table marker (like "📊 TABLE 1")
      const isTableMarker = /^[\s]*[📊]*[\s]*TABLE\s*\d+[:]/i.test(line);
      
      if (isTableLine || isTableMarker) {
        // If we hit a table marker, flush any pending table first
        if (isTableMarker && tableLines.length > 0) {
          flushTable();
        }
        tableLines.push(line);
      } else {
        // If we have table lines and hit non-table content, flush the table
        if (tableLines.length > 0) {
          flushTable();
        }
        
        // Handle escaped newlines (replace \n with actual newlines)
        let processedLine = line.replace(/\\n/g, '\n');
        
        // Regular text formatting
        if (/^[\d•\-\*]/.test(processedLine.trim())) {
          elements.push(<p key={i} className="mb-2 text-slate-200 whitespace-pre-wrap">{processedLine}</p>);
        } else if (processedLine.trim() === '') {
          elements.push(<br key={i} />);
        } else if (/^EXPLANATION:/i.test(processedLine.trim())) {
          // Special formatting for explanation headers
          elements.push(
            <div key={i} className="mt-6 mb-4">
              <h3 className="text-lg font-semibold text-blue-400 mb-2">{processedLine}</h3>
            </div>
          );
        } else if (/^📊\s*TABLE\s*\d+/i.test(processedLine.trim())) {
          // Special formatting for table headers
          elements.push(
            <div key={i} className="mt-8 mb-3">
              <h2 className="text-xl font-bold text-emerald-400">{processedLine}</h2>
            </div>
          );
        } else {
          // Regular paragraphs with better spacing
          elements.push(<p key={i} className="mb-4 text-slate-200 whitespace-pre-wrap break-words leading-relaxed">{processedLine}</p>);
        }
      }
    }
    
    // Flush any remaining table lines
    flushTable();

    return elements;
  };

  return (
    <div className="rounded-xl border border-slate-950/40 bg-slate-900/50 backdrop-blur-sm shadow-xl shadow-slate-950/50 overflow-hidden">
      {/* Tabs */}
      <div className="border-b border-slate-950/40 bg-slate-800/30">
        <div className="flex overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 px-4 py-3 text-sm font-medium transition-colors duration-200 whitespace-nowrap flex items-center justify-center gap-2 ${
                activeTab === tab.id
                  ? "bg-slate-900/50 text-blue-400 border-b-2 border-blue-500"
                  : "text-slate-400 hover:text-white hover:bg-slate-800/50"
              }`}
            >
              <span className="flex-shrink-0">{tab.icon}</span>
              <span className="hidden sm:inline">{tab.label}</span>
              <span className="sm:hidden">{tab.label.split(" ")[0]}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="p-6 max-h-[70vh] overflow-y-auto">
        <div className="prose max-w-none">
          <div className="text-slate-200 leading-relaxed">
            {formatText(solution[activeTab])}
          </div>
        </div>

        {/* Retrieved IDs */}
        {solution.retrieved_ids && solution.retrieved_ids.length > 0 && (
          <div className="mt-6 pt-6 border-t border-slate-950/40">
            <p className="text-sm text-slate-400 mb-2">Similar problems used:</p>
            <div className="flex flex-wrap gap-2">
              {solution.retrieved_ids.map((id, idx) => (
                <span
                  key={idx}
                  className="px-2 py-1 bg-blue-900/50 text-blue-300 text-xs rounded border border-blue-800/50"
                >
                  {id}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

