import { Link } from 'react-router-dom'
import { Search, Database, ArrowRight, MessageSquare, BarChart3, FileText, Network, Sparkles, Zap, ShieldCheck } from 'lucide-react'

export default function Home() {
  return (
    <div className="relative overflow-hidden">
      {/* Floating gradient orbs */}
      <div className="pointer-events-none absolute -top-20 left-1/4 w-72 h-72 bg-indigo-600/20 rounded-full blur-[100px] animate-float" />
      <div className="pointer-events-none absolute top-40 right-1/4 w-80 h-80 bg-purple-600/20 rounded-full blur-[100px] animate-float-delayed" />
      <div className="pointer-events-none absolute top-96 left-1/3 w-64 h-64 bg-fuchsia-600/10 rounded-full blur-[100px] animate-float" />

      <div className="relative max-w-7xl mx-auto px-6 py-16">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto animate-fade-in-up">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full glass-card text-xs font-semibold text-indigo-300 mb-6">
            <Sparkles size={13} className="text-amber-300" />
            Exercise 2 — NLP QA &amp; Chatbot System
          </div>
          <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight leading-[1.1]">
            <span className="text-white">Intelligent</span>{' '}
            <span className="text-gradient">QA &amp; Chatbot</span>
            <br className="hidden md:block" />
            <span className="text-white">System</span>
          </h1>
          <p className="mt-5 text-lg text-slate-400 max-w-xl mx-auto">
            Information Retrieval + Knowledge-Based Question Answering, wired together
            with real dialogue management and measurable evaluation.
          </p>

          <div className="mt-7 flex flex-wrap items-center justify-center gap-3 text-xs text-slate-400">
            <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/5 border border-white/10">
              <Zap size={12} className="text-amber-300" /> Real TF-IDF retrieval
            </span>
            <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/5 border border-white/10">
              <Database size={12} className="text-purple-300" /> CSV knowledge base
            </span>
            <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/5 border border-white/10">
              <ShieldCheck size={12} className="text-emerald-300" /> Computed evaluation
            </span>
          </div>
        </div>

        {/* Two main cards */}
        <div className="grid md:grid-cols-2 gap-6 mt-16">
          <Link
            to="/ir-qa"
            className="group relative glass-card rounded-2xl p-8 overflow-hidden hover:border-indigo-400/40 transition-all duration-300 hover:-translate-y-1.5 hover:shadow-glow"
          >
            <div className="absolute -top-24 -right-24 w-64 h-64 bg-indigo-500/20 rounded-full blur-3xl group-hover:bg-indigo-500/30 group-hover:scale-110 transition-all duration-500" />
            <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 animate-shimmer" />
            <div className="relative">
              <div className="flex items-center justify-between">
                <div className="w-[52px] h-[52px] rounded-2xl bg-gradient-to-br from-indigo-500 to-blue-500 flex items-center justify-center shadow-glow group-hover:scale-110 group-hover:-rotate-3 transition-all duration-300">
                  <Search size={24} className="text-white" />
                </div>
                <span className="text-[10px] font-bold uppercase tracking-widest text-indigo-400/70">Mode 01</span>
              </div>
              <h2 className="text-2xl font-bold text-white mt-5">IR-Based QA</h2>
              <p className="mt-3 text-slate-400 leading-relaxed text-[15px]">
                Ask questions and retrieve factoid answers from unstructured documents using
                information retrieval (TF-IDF + cosine similarity) and extractive question answering.
              </p>
              <div className="mt-6 flex items-center gap-2 text-indigo-300 font-semibold text-sm">
                Open IR-Based QA <ArrowRight size={16} className="group-hover:translate-x-1.5 transition-transform" />
              </div>
            </div>
          </Link>

          <Link
            to="/knowledge-qa"
            className="group relative glass-card rounded-2xl p-8 overflow-hidden hover:border-purple-400/40 transition-all duration-300 hover:-translate-y-1.5 hover:shadow-glow"
          >
            <div className="absolute -top-24 -right-24 w-64 h-64 bg-purple-500/20 rounded-full blur-3xl group-hover:bg-purple-500/30 group-hover:scale-110 transition-all duration-500" />
            <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 animate-shimmer" />
            <div className="relative">
              <div className="flex items-center justify-between">
                <div className="w-[52px] h-[52px] rounded-2xl bg-gradient-to-br from-purple-500 to-fuchsia-500 flex items-center justify-center shadow-glow group-hover:scale-110 group-hover:rotate-3 transition-all duration-300">
                  <Database size={24} className="text-white" />
                </div>
                <span className="text-[10px] font-bold uppercase tracking-widest text-purple-400/70">Mode 02</span>
              </div>
              <h2 className="text-2xl font-bold text-white mt-5">Knowledge-Based QA</h2>
              <p className="mt-3 text-slate-400 leading-relaxed text-[15px]">
                Ask questions against a structured healthcare knowledge base (CSV-backed) and retrieve
                answers about symptoms, causes, treatment, and specialists via entity and relation queries.
              </p>
              <div className="mt-6 flex items-center gap-2 text-purple-300 font-semibold text-sm">
                Open Knowledge QA <ArrowRight size={16} className="group-hover:translate-x-1.5 transition-transform" />
              </div>
            </div>
          </Link>
        </div>

        {/* Secondary links */}
        <div className="grid sm:grid-cols-2 gap-4 mt-6">
          <Link to="/chat" className="group glass-card rounded-xl p-5 flex items-center gap-4 hover:border-emerald-400/30 transition-all duration-300 hover:-translate-y-0.5">
            <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-emerald-500/20 to-teal-500/20 flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
              <MessageSquare size={19} className="text-emerald-400" />
            </div>
            <div>
              <p className="font-semibold text-white text-sm">Chat Assistant</p>
              <p className="text-xs text-slate-500">Conversational dialogue with context memory</p>
            </div>
            <ArrowRight size={15} className="ml-auto text-slate-600 group-hover:text-emerald-400 group-hover:translate-x-1 transition-all" />
          </Link>
          <Link to="/evaluation" className="group glass-card rounded-xl p-5 flex items-center gap-4 hover:border-amber-400/30 transition-all duration-300 hover:-translate-y-0.5">
            <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-amber-500/20 to-orange-500/20 flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
              <BarChart3 size={19} className="text-amber-400" />
            </div>
            <div>
              <p className="font-semibold text-white text-sm">Evaluation</p>
              <p className="text-xs text-slate-500">EM / F1 / Accuracy computed on real test data</p>
            </div>
            <ArrowRight size={15} className="ml-auto text-slate-600 group-hover:text-amber-400 group-hover:translate-x-1 transition-all" />
          </Link>
        </div>

        {/* How it works */}
        <div className="mt-20">
          <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider text-center mb-8">
            How the system works
          </h3>
          <div className="grid md:grid-cols-4 gap-4">
            {[
              { icon: FileText, title: '1. Sources', desc: 'Document corpus + healthcare knowledge base', color: 'text-sky-400' },
              { icon: Search, title: '2. Retrieval', desc: 'TF-IDF ranking & entity/relation detection', color: 'text-indigo-400' },
              { icon: Network, title: '3. Answering', desc: 'Extractive QA & KB lookup with evidence', color: 'text-purple-400' },
              { icon: MessageSquare, title: '4. Dialogue', desc: 'Context-aware follow-up questions', color: 'text-emerald-400' },
            ].map(({ icon: Icon, title, desc, color }, i) => (
              <div
                key={title}
                className="group glass-card rounded-xl p-5 text-center hover:-translate-y-1 hover:border-white/20 transition-all duration-300 animate-fade-in-up"
                style={{ animationDelay: `${i * 80}ms` }}
              >
                <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform">
                  <Icon size={19} className={color} />
                </div>
                <p className="font-semibold text-white text-sm">{title}</p>
                <p className="text-xs text-slate-500 mt-1.5">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
