import React, { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { ChevronLeft, ChevronRight, Terminal } from 'lucide-react';
import { getDemoCategories, getDemoCategoryResults, DemoCategory, DemoCategoryResponse, DemoQueryResult } from '../services/apiService';
import { SQLDisplay } from './SQLDisplay';
import { ResultsTable } from './ResultsTable';

interface QueryPresentation {
  categoryId: string;
  categoryLabel: string;
  section: string;
  query: DemoQueryResult;
}

export function DemoPanel() {
  const [categories, setCategories] = useState<DemoCategory[]>([]);
  const [queries, setQueries] = useState<QueryPresentation[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDemoData();
  }, []);

  useEffect(() => {
    const handleKeyboard = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight') handleNext();
      if (e.key === 'ArrowLeft') handlePrev();
    };

    window.addEventListener('keydown', handleKeyboard);
    return () => window.removeEventListener('keydown', handleKeyboard);
  }, [currentIndex, queries.length]);

  const loadDemoData = async () => {
    try {
      setLoading(true);
      const { categories: cats } = await getDemoCategories();
      setCategories(cats);

      const allResults = await Promise.all(
        cats.map(cat => getDemoCategoryResults(cat.id))
      );

      const flatQueries: QueryPresentation[] = [];
      allResults.forEach(catData => {
        catData.queries.forEach(query => {
          flatQueries.push({
            categoryId: catData.category,
            categoryLabel: catData.label,
            section: catData.section,
            query,
          });
        });
      });

      setQueries(flatQueries);
      setLoading(false);
    } catch (err: any) {
      setError(err.message || 'Failed to load demo data');
      setLoading(false);
    }
  };

  const handlePrev = () => {
    if (currentIndex > 0) setCurrentIndex(currentIndex - 1);
  };

  const handleNext = () => {
    if (currentIndex < queries.length - 1) setCurrentIndex(currentIndex + 1);
  };

  const jumpToCategory = (categoryId: string) => {
    const idx = queries.findIndex(q => q.categoryId === categoryId);
    if (idx !== -1) setCurrentIndex(idx);
  };

  if (loading) {
    return (
      <motion.div
        key="dbms-loading"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex h-full items-center justify-center"
      >
        <div className="flex items-center gap-3 text-cyan-400 font-mono">
          <div className="h-2 w-2 animate-bounce rounded-full bg-cyan-400" />
          <div className="h-2 w-2 animate-bounce rounded-full bg-cyan-400 [animation-delay:0.2s]" />
          <div className="h-2 w-2 animate-bounce rounded-full bg-cyan-400 [animation-delay:0.4s]" />
          <span className="ml-2 text-sm text-cyan-200/70">$ loading demo queries...</span>
        </div>
      </motion.div>
    );
  }

  if (error) {
    return (
      <motion.div
        key="dbms-error"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex h-full items-center justify-center"
      >
        <div className="rounded-lg border border-red-500/30 bg-red-900/20 px-6 py-4 text-red-300 backdrop-blur-xl font-mono">
          <span className="text-red-400">ERROR:</span> {error}
        </div>
      </motion.div>
    );
  }

  if (queries.length === 0) {
    return (
      <motion.div
        key="dbms-empty"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex h-full items-center justify-center text-cyan-300/50 font-mono"
      >
        $ no demo queries available
      </motion.div>
    );
  }

  const currentQuery = queries[currentIndex];
  const sectionColor = getSectionColor(currentQuery.section);

  return (
    <motion.div
      key="dbms"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="flex flex-col h-full"
    >
      {/* Top Bar - Terminal style header */}
      <div className="flex-shrink-0 flex items-center justify-between bg-slate-800 px-4 py-2 rounded-t-lg border border-cyan-500/20 border-b-0">
        <div className="flex items-center gap-4">
          {/* Window controls */}
          <div className="flex gap-1.5">
            <div className="w-3 h-3 rounded-full bg-red-500/80" />
            <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
            <div className="w-3 h-3 rounded-full bg-green-500/80" />
          </div>

          {/* Categories as terminal tabs */}
          <div className="flex flex-wrap gap-1">
            {categories.map(cat => {
              const isActive = queries.find((q, idx) => idx === currentIndex)?.categoryId === cat.id;
              return (
                <button
                  key={cat.id}
                  onClick={() => jumpToCategory(cat.id)}
                  className={`rounded px-2 py-1 text-xs font-mono transition-all ${
                    isActive
                      ? 'bg-cyan-500/30 text-cyan-300 border border-cyan-400/30'
                      : 'text-cyan-400/60 hover:text-cyan-300 hover:bg-cyan-500/10'
                  }`}
                >
                  {cat.label}
                </button>
              );
            })}
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-xs text-cyan-400/60 font-mono">
            [{currentIndex + 1}/{queries.length}]
          </span>
          <div className="flex gap-1">
            <button
              onClick={handlePrev}
              disabled={currentIndex === 0}
              className="flex h-6 w-6 items-center justify-center rounded border border-cyan-500/20 bg-slate-700/50 text-cyan-300 transition-all hover:bg-cyan-500/20 disabled:opacity-30"
            >
              <ChevronLeft size={14} />
            </button>
            <button
              onClick={handleNext}
              disabled={currentIndex === queries.length - 1}
              className="flex h-6 w-6 items-center justify-center rounded border border-cyan-500/20 bg-slate-700/50 text-cyan-300 transition-all hover:bg-cyan-500/20 disabled:opacity-30"
            >
              <ChevronRight size={14} />
            </button>
          </div>
        </div>
      </div>

      {/* Main Content Area - Split Layout (25% SQL / 75% Results) */}
      <div className="flex-1 grid grid-cols-12 gap-0 min-h-0 overflow-hidden border border-cyan-500/20 border-t-0 rounded-b-lg bg-slate-900/80 backdrop-blur-xl">
        {/* Left Column: Query Info & SQL (25%) - Compact */}
        <div className="col-span-3 flex flex-col border-r border-cyan-500/20 overflow-hidden">
          {/* Query Header */}
          <motion.div
            key={currentIndex}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex-shrink-0 p-3 border-b border-cyan-500/10"
          >
            <div className="flex items-center gap-2 mb-2">
              <span className={`inline-block rounded px-2 py-0.5 text-xs font-mono font-semibold ${sectionColor}`}>
                {currentQuery.section}
              </span>
            </div>
            <h3 className="text-sm font-bold text-white line-clamp-1">{currentQuery.query.title}</h3>
            <p className="text-xs text-cyan-300/60 line-clamp-2 mt-1">{currentQuery.query.question}</p>
          </motion.div>

          {/* SQL Query - Compact with scroll */}
          <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
            <div className="px-3 py-2 text-xs font-mono text-cyan-500/60 flex items-center gap-2 border-b border-cyan-500/10 flex-shrink-0">
              <Terminal size={12} />
              <span>SQL Query</span>
            </div>
            <div className="flex-1 overflow-y-auto custom-scrollbar">
              <SQLDisplay sql={currentQuery.query.sql} />
            </div>
          </div>
        </div>

        {/* Right Column: Results (75%) - Larger */}
        <div className="col-span-9 flex flex-col overflow-hidden">
          {/* Results Header */}
          <div className="flex items-center justify-between px-4 py-2 border-b border-cyan-500/10 flex-shrink-0">
            <div className="flex items-center gap-2 text-xs font-mono">
              <span className="text-green-400">$</span>
              <span className="text-cyan-400">Query Results</span>
            </div>
            {!currentQuery.query.error && currentQuery.query.rows.length > 0 && (
              <span className="rounded bg-cyan-500/20 px-2 py-0.5 text-xs font-mono text-cyan-300">
                {currentQuery.query.row_count} rows
              </span>
            )}
          </div>

          {/* Results Content */}
          <motion.div
            key={currentIndex}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex-1 min-h-0 overflow-hidden"
          >
            {currentQuery.query.error ? (
              <div className="flex items-center justify-center h-full px-6 py-4">
                <div className="text-center font-mono">
                  <div className="text-red-400 text-2xl mb-2">✗</div>
                  <div className="text-red-300 text-sm">{currentQuery.query.error}</div>
                </div>
              </div>
            ) : currentQuery.query.rows.length > 0 ? (
              <ResultsTable
                columns={currentQuery.query.columns}
                rows={currentQuery.query.rows.map(row => {
                  const obj: any = {};
                  currentQuery.query.columns.forEach((col, idx) => {
                    obj[col] = row[idx];
                  });
                  return obj;
                })}
              />
            ) : (
              <div className="flex items-center justify-center h-full font-mono">
                <div className="text-center">
                  <div className="text-cyan-500/40 text-2xl mb-2">∅</div>
                  <div className="text-cyan-400/40 text-sm">Query returned no rows</div>
                </div>
              </div>
            )}
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
}

function getSectionColor(section: string): string {
  // Cyan/Teal/Blue color palette for sections
  const colors: Record<string, string> = {
    '1.1': 'bg-cyan-500/30 text-cyan-200 border border-cyan-400/30',
    '1.2': 'bg-teal-500/30 text-teal-200 border border-teal-400/30',
    '1.3': 'bg-blue-500/30 text-blue-200 border border-blue-400/30',
    '1.4': 'bg-sky-500/30 text-sky-200 border border-sky-400/30',
    '1.5': 'bg-indigo-500/30 text-indigo-200 border border-indigo-400/30',
    '1.6': 'bg-cyan-600/30 text-cyan-200 border border-cyan-400/30',
    '1.7': 'bg-teal-600/30 text-teal-200 border border-teal-400/30',
    '1.8': 'bg-blue-600/30 text-blue-200 border border-blue-400/30',
    '1.9': 'bg-sky-600/30 text-sky-200 border border-sky-400/30',
    '1.10': 'bg-indigo-600/30 text-indigo-200 border border-indigo-400/30',
  };

  return colors[section] || 'bg-cyan-500/30 text-cyan-200 border border-cyan-400/30';
}