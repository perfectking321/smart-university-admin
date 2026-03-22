import React from 'react';
import { Copy, Check } from 'lucide-react';
import { useState } from 'react';

interface SQLDisplayProps {
  sql: string;
}

export const SQLDisplay: React.FC<SQLDisplayProps> = ({ sql }) => {
  const [copied, setCopied] = useState(false);

  const copyToClipboard = () => {
    navigator.clipboard.writeText(sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative group p-3 font-mono text-sm">
      {/* Terminal prompt */}
      <div className="flex items-center gap-2 text-cyan-500/60 text-xs mb-2">
        <span className="text-green-400">mysql{'>'}</span>
        <span className="text-cyan-400/40">executing query...</span>
      </div>

      {/* Copy button */}
      <div className="absolute right-2 top-2 opacity-0 group-hover:opacity-100 transition-opacity">
        <button
          onClick={copyToClipboard}
          className={`flex items-center gap-1.5 rounded px-2 py-1 text-xs transition-all ${
            copied
              ? 'bg-green-500/20 border border-green-500/30 text-green-400'
              : 'bg-cyan-500/20 border border-cyan-500/30 text-cyan-300 hover:bg-cyan-500/30'
          }`}
        >
          {copied ? <Check size={12} /> : <Copy size={12} />}
          {copied ? 'Copied!' : 'Copy'}
        </button>
      </div>

      {/* SQL Code */}
      <pre className="overflow-x-auto whitespace-pre-wrap leading-relaxed">
        {sql.split('\n').map((line, i) => {
          // Terminal-style syntax highlighting
          const highlighted = line
            // SQL Keywords - Cyan/Teal
            .replace(/\b(SELECT|FROM|WHERE|JOIN|LEFT|RIGHT|INNER|OUTER|ON|GROUP BY|HAVING|ORDER BY|LIMIT|AND|OR|IN|AS|NOT|NULL|IS|LIKE|BETWEEN|EXISTS|UNION|ALL|DISTINCT|INTO|VALUES|INSERT|UPDATE|DELETE|CREATE|TABLE|INDEX|DROP|ALTER|ADD|SET|ASC|DESC|CASE|WHEN|THEN|ELSE|END|WITH|OVER|PARTITION|BY)\b/gi, '<span class="text-cyan-400 font-semibold">$1</span>')
            // Functions - Teal
            .replace(/\b(AVG|COUNT|SUM|MIN|MAX|ROUND|COALESCE|CONCAT|UPPER|LOWER|LENGTH|SUBSTRING|TRIM|NOW|DATE|YEAR|MONTH|DAY|HOUR|MINUTE|SECOND|CAST|CONVERT|IFNULL|NULLIF|ROW_NUMBER|RANK|DENSE_RANK)\b/gi, '<span class="text-teal-400">$1</span>')
            // Strings - Green
            .replace(/('[^']*')/g, '<span class="text-green-400">$1</span>')
            // Numbers - Amber
            .replace(/\b(\d+\.?\d*)\b/g, '<span class="text-amber-400">$1</span>')
            // Table/Column names after FROM, JOIN, etc (simplified)
            .replace(/\b(students|courses|departments|attendance|placements|instructors|enrollments)\b/gi, '<span class="text-blue-400">$1</span>');

          return (
            <div key={i} className="text-cyan-100/80" dangerouslySetInnerHTML={{ __html: highlighted }} />
          );
        })}
      </pre>
    </div>
  );
};