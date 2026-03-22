import React from 'react';

interface ResultsTableProps {
  columns: string[];
  rows: any[];
}

export const ResultsTable: React.FC<ResultsTableProps> = ({ columns, rows }) => {
  if (!columns.length) return null;

  return (
    <div className="h-full overflow-auto custom-scrollbar font-mono text-sm">
      <table className="w-full text-left">
        <thead className="bg-slate-800/80 text-xs uppercase tracking-wider text-cyan-400 sticky top-0">
          <tr>
            <th className="px-3 py-2 border-b border-cyan-500/20 text-cyan-500/60 w-10">#</th>
            {columns.map((col) => (
              <th key={col} className="px-3 py-2 border-b border-cyan-500/20">
                {col.replace(/_/g, ' ')}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-cyan-500/10">
          {rows.map((row, idx) => (
            <tr key={idx} className="hover:bg-cyan-500/5 transition-colors group">
              <td className="px-3 py-2 text-cyan-500/40 text-xs">{idx + 1}</td>
              {columns.map((col) => (
                <td key={col} className="px-3 py-2 text-cyan-100/90 group-hover:text-cyan-50">
                  {formatValue(row[col])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// Format values with terminal-style coloring
function formatValue(value: any): React.ReactNode {
  if (value === null || value === undefined) {
    return <span className="text-cyan-500/40 italic">NULL</span>;
  }

  const strValue = value.toString();

  // Numbers - yellow/amber color
  if (typeof value === 'number' || !isNaN(Number(strValue))) {
    return <span className="text-amber-400">{strValue}</span>;
  }

  // Booleans
  if (typeof value === 'boolean' || strValue === 'true' || strValue === 'false') {
    return <span className={value ? 'text-green-400' : 'text-red-400'}>{strValue}</span>;
  }

  // Dates (simple detection)
  if (strValue.match(/^\d{4}-\d{2}-\d{2}/)) {
    return <span className="text-teal-400">{strValue}</span>;
  }

  // Default string - cyan
  return <span className="text-cyan-100">{strValue}</span>;
}