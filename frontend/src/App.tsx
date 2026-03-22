import React, { useState, useRef, useEffect } from 'react';
import { Bot, Database, Send, Sparkles, Terminal, LayoutGrid } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { ChatMessage, QueryResult } from './types';
import { queryDatabase } from './services/apiService';
import { SQLDisplay } from './components/SQLDisplay';
import { ResultsTable } from './components/ResultsTable';
import { DemoPanel } from './components/DemoPanel';
import { SplineHero } from './components/SplineHero';
import DarkVeil from './components/DarkVeil';
import type { Application } from '@splinetool/runtime';

export default function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hey! Admin, What can I help with?',
    }
  ]);
  const [latestResult, setLatestResult] = useState<{ sql?: string; results?: QueryResult } | null>(null);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [splineApp, setSplineApp] = useState<Application | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Refs for smooth scrolling
  const heroRef = useRef<HTMLDivElement>(null);
  const chatRef = useRef<HTMLDivElement>(null);
  const demoRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const scrollToSection = (ref: React.RefObject<HTMLDivElement>) => {
    ref.current?.scrollIntoView({
      behavior: 'smooth',
      block: 'start'
    });
  };

  const handleSplineLoad = (app: Application) => {
    setSplineApp(app);
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);

    try {
      const response = await queryDatabase(input);
      const results: QueryResult = {
        columns: response.results.columns || [],
        rows: response.results.rows || [],
      };

      const statusContent = results.rows.length > 0
        ? `Query executed successfully! Found ${results.rows.length} rows.${response.cached ? ' (cached)' : ''}`
        : 'Query executed but returned no results.';

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: statusContent,
      };

      setMessages(prev => [...prev, assistantMessage]);
      setLatestResult({ sql: response.sql, results });
    } catch (error: any) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Error: ${error.message}`,
      };
      setMessages(prev => [...prev, errorMessage]);
      setLatestResult(null);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="min-h-screen w-full bg-black text-zinc-100 overflow-x-hidden">
      {/* Floating Navigation - Cyan/Teal theme */}
      <nav className="fixed top-6 left-1/2 transform -translate-x-1/2 z-50">
        <div className="flex items-center gap-2 bg-black/40 backdrop-blur-md border border-cyan-500/20 rounded-full px-4 py-2">
          <button
            onClick={() => scrollToSection(heroRef)}
            className="px-4 py-2 text-sm font-medium text-white/70 hover:text-white transition-colors rounded-full hover:bg-cyan-500/10"
          >
            Home
          </button>
          <button
            onClick={() => scrollToSection(chatRef)}
            className="px-4 py-2 text-sm font-medium text-white/70 hover:text-white transition-colors rounded-full hover:bg-cyan-500/10"
          >
            Chat
          </button>
          <button
            onClick={() => scrollToSection(demoRef)}
            className="px-4 py-2 text-sm font-medium text-white/70 hover:text-white transition-colors rounded-full hover:bg-cyan-500/10"
          >
            Demo
          </button>
        </div>
      </nav>

      {/* Hero Section - Full Immersive 3D (NO Dark Veil) */}
      <section ref={heroRef} className="relative w-full h-screen bg-black">
        <SplineHero onLoad={handleSplineLoad} onStartQuerying={() => scrollToSection(chatRef)} />

        {/* Minimal branding overlay - Cyan theme */}
        <div className="absolute top-6 left-6 z-40">
          <div className="flex items-center gap-2 text-white/80">
            <div className="w-8 h-8 bg-cyan-500/20 border border-cyan-400/30 rounded-lg flex items-center justify-center">
              <LayoutGrid size={16} />
            </div>
            <span className="text-sm font-medium">Smart University Admin</span>
          </div>
        </div>
      </section>

      {/* Chat Section - With Dark Veil Background & Terminal UI */}
      <section ref={chatRef} className="h-screen flex flex-col relative overflow-hidden">
        {/* Dark Veil Background for this section */}
        <div className="absolute inset-0 z-0">
          <DarkVeil />
        </div>

        {/* Content */}
        <div className="relative z-10 flex flex-col h-full">
          <div className="flex-shrink-0 text-center py-6">
            <h2 className="text-3xl font-light text-white mb-2">Query Chat Mode</h2>
            <p className="text-cyan-200/60 text-base max-w-xl mx-auto">
              Ask questions in plain English and get instant SQL results
            </p>
          </div>

          {/* Chat Interface - Full Height */}
          <div className="flex-1 max-w-7xl mx-auto w-full px-6 pb-6 min-h-0">
            <div className="grid grid-cols-2 gap-6 h-full">
              {/* Left Column: Chat History */}
              <div className="flex flex-col min-h-0">
                <div className="flex-1 overflow-y-auto space-y-4 custom-scrollbar pr-2" ref={scrollRef}>
                  {messages.length === 1 && (
                    <div className="space-y-4">
                      <h3 className="text-2xl font-light text-cyan-200/70 leading-tight">
                        Hey! Admin,<br />
                        <span className="text-white">What can I help with?</span>
                      </h3>
                      <div className="rounded-lg bg-slate-900/60 border border-cyan-500/20 p-4 backdrop-blur-xl font-mono">
                        <div className="flex items-center gap-2 text-cyan-400 mb-3">
                          <Terminal size={14} />
                          <span className="text-xs font-semibold uppercase tracking-wider">AI Assistant</span>
                        </div>
                        <ul className="space-y-2 text-sm text-cyan-200/70">
                          <li className="hover:text-cyan-300 cursor-pointer transition-colors">$ Show all students in Computer Science</li>
                          <li className="hover:text-cyan-300 cursor-pointer transition-colors">$ What is the average GPA by department?</li>
                          <li className="hover:text-cyan-300 cursor-pointer transition-colors">$ List students with attendance below 75%</li>
                        </ul>
                      </div>
                    </div>
                  )}

                  <div className="space-y-3">
                    {messages.map((msg) => (
                      <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className="flex items-start gap-3 max-w-[85%]">
                          {msg.role === 'assistant' && (
                            <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
                              <Bot size={16} />
                            </div>
                          )}
                          <div className={`rounded-lg px-4 py-3 shadow-lg backdrop-blur-xl font-mono text-sm ${
                            msg.role === 'user'
                              ? 'bg-teal-600/30 border border-teal-400/30 text-teal-50'
                              : 'bg-slate-900/60 border border-cyan-500/20 text-cyan-100'
                          }`}>
                            {msg.role === 'user' && <span className="text-teal-400 mr-2">{'>'}</span>}
                            {msg.content}
                          </div>
                        </div>
                      </div>
                    ))}
                    {isTyping && (
                      <div className="flex items-center gap-2 text-cyan-400/50 ml-10 font-mono text-sm">
                        <span className="text-cyan-500">$</span>
                        <div className="h-1.5 w-1.5 animate-bounce rounded-full bg-cyan-400/50" />
                        <div className="h-1.5 w-1.5 animate-bounce rounded-full bg-cyan-400/50 [animation-delay:0.2s]" />
                        <div className="h-1.5 w-1.5 animate-bounce rounded-full bg-cyan-400/50 [animation-delay:0.4s]" />
                      </div>
                    )}
                  </div>
                </div>

                {/* Chat Input - Terminal style */}
                <div className="flex-shrink-0 mt-4">
                  <div className="relative rounded-lg border border-cyan-500/30 bg-slate-900/80 p-2 shadow-lg backdrop-blur-xl">
                    <div className="flex items-center gap-2 px-3 py-2">
                      <span className="text-cyan-500 font-mono font-bold">$</span>
                      <input
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                        placeholder="Enter your query..."
                        className="flex-1 bg-transparent text-cyan-100 placeholder:text-cyan-500/40 focus:outline-none text-sm font-mono"
                      />
                      <button
                        onClick={handleSend}
                        disabled={!input.trim()}
                        className="flex h-8 items-center gap-1.5 rounded bg-gradient-to-r from-cyan-600 to-teal-600 px-4 text-xs font-semibold text-white transition-all hover:from-cyan-500 hover:to-teal-500 disabled:opacity-50 shadow-[0_0_15px_rgba(6,182,212,0.3)]"
                      >
                        Run
                        <Send size={12} />
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {/* Right Column: Terminal Results */}
              <div className="flex flex-col min-h-0">
                {latestResult ? (
                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="flex flex-col h-full space-y-3"
                  >
                    {/* Terminal Window Header */}
                    <div className="rounded-t-lg bg-slate-800 border border-cyan-500/20 border-b-0 px-4 py-2 flex items-center gap-2">
                      <div className="flex gap-1.5">
                        <div className="w-3 h-3 rounded-full bg-red-500/80" />
                        <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                        <div className="w-3 h-3 rounded-full bg-green-500/80" />
                      </div>
                      <span className="text-xs text-cyan-300/60 font-mono ml-2">query_results.sql</span>
                    </div>

                    {latestResult.sql && (
                      <div className="flex-shrink-0">
                        <div className="rounded-none border border-cyan-500/20 border-t-0 bg-slate-900/90 backdrop-blur-xl">
                          <SQLDisplay sql={latestResult.sql} />
                        </div>
                      </div>
                    )}

                    {latestResult.results && latestResult.results.rows.length > 0 && (
                      <div className="flex-1 flex flex-col min-h-0">
                        <div className="text-xs font-mono text-cyan-400 px-2 py-1 flex items-center gap-2">
                          <span className="text-green-400">✓</span>
                          <span>OUTPUT: {latestResult.results.rows.length} rows returned</span>
                        </div>
                        <div className="flex-1 rounded-b-lg overflow-hidden border border-cyan-500/20 bg-slate-900/90 backdrop-blur-xl">
                          <ResultsTable columns={latestResult.results.columns} rows={latestResult.results.rows} />
                        </div>
                      </div>
                    )}
                  </motion.div>
                ) : (
                  <div className="flex flex-col h-full rounded-lg border border-dashed border-cyan-500/20 bg-slate-900/40 backdrop-blur-sm">
                    {/* Empty Terminal Window */}
                    <div className="rounded-t-lg bg-slate-800 px-4 py-2 flex items-center gap-2">
                      <div className="flex gap-1.5">
                        <div className="w-3 h-3 rounded-full bg-red-500/40" />
                        <div className="w-3 h-3 rounded-full bg-yellow-500/40" />
                        <div className="w-3 h-3 rounded-full bg-green-500/40" />
                      </div>
                      <span className="text-xs text-cyan-300/40 font-mono ml-2">terminal</span>
                    </div>
                    <div className="flex-1 flex items-center justify-center">
                      <div className="text-center font-mono">
                        <Terminal size={32} className="mx-auto mb-3 text-cyan-500/30" />
                        <p className="text-cyan-400/40 text-sm">$ waiting for query...</p>
                        <p className="text-cyan-500/30 text-xs mt-1">_</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Demo Section - With Dark Veil Background */}
      <section ref={demoRef} className="h-screen flex flex-col relative overflow-hidden">
        {/* Dark Veil Background for this section */}
        <div className="absolute inset-0 z-0">
          <DarkVeil />
        </div>

        {/* Content */}
        <div className="relative z-10 flex flex-col h-full">
          <div className="flex-shrink-0 text-center py-6">
            <h2 className="text-3xl font-light text-white mb-2">DBMS Demo Mode</h2>
            <p className="text-cyan-200/60 text-base max-w-xl mx-auto">
              Explore pre-built queries organized by category
            </p>
          </div>

          <div className="flex-1 max-w-7xl mx-auto w-full px-6 pb-6 min-h-0">
            <DemoPanel />
          </div>
        </div>
      </section>
    </div>
  );
}