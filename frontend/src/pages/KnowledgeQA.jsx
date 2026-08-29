import { useState } from 'react'
import { Database, Loader2, AlertCircle, RotateCcw, Link2 } from 'lucide-react'
import { api } from '../services/api'
import PipelineSteps from '../components/PipelineSteps'

const EXAMPLES = [
  'What are the symptoms of Diabetes?',
  'Which doctor should I see for Migraine?',
  'How is Asthma treated?',
  'What causes Hypertension?',
  'How can I prevent Chickenpox?',
]

export default function KnowledgeQA() {
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const ask = async (q) => {
    const query = (q ?? question).trim()
    if (!query) return
    setLoading(true)
    setError(null)
    try {
      const data = await api.askKB(query)
      setResult(data)
      setQuestion(query)
    } catch (e) {
      setError(e.message)
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  const reset = () => {
    setQuestion('')
    setResult(null)
    setError(null)
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      <div className="flex items-center gap-3 mb-1">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-purple-500 to-fuchsia-500 flex items-center justify-center">
          <Database size={17} className="text-white" />
        </div>
        <h1 className="text-2xl font-bold text-white">Knowledge-Based QA</h1>
      </div>
      <p className="text-slate-400 text-sm ml-12">
        Question → Entity/Relation Detection → Knowledge Base Query → Answer
      </p>

      <div className="glass-card rounded-2xl p-6 mt-8">
        <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">Ask the Knowledge Base</label>
        <div className="mt-2 flex gap-3">
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && ask()}
            placeholder="e.g. What are the symptoms of Diabetes?"
            className="flex-1 bg-navy-900/70 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-slate-600 outline-none focus:border-purple-400/50 focus:ring-2 focus:ring-purple-500/20 transition-all"
          />
          <button
            onClick={() => ask()}
            disabled={loading}
            className="px-5 py-3 rounded-xl bg-gradient-to-br from-purple-500 to-fuchsia-600 text-white font-medium hover:brightness-110 hover:shadow-glow active:scale-95 transition-all duration-200 disabled:opacity-50 flex items-center gap-2 shrink-0"
          >
            {loading ? <Loader2 size={16} className="animate-spin" /> : <Database size={16} />}
            Query Knowledge Base
          </button>
          <button
            onClick={reset}
            className="px-3.5 py-3 rounded-xl border border-white/10 text-slate-400 hover:text-white hover:bg-white/5 transition-all shrink-0"
            title="Clear"
          >
            <RotateCcw size={16} />
          </button>
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          {EXAMPLES.map((ex) => (
            <button
              key={ex}
              onClick={() => ask(ex)}
              className="text-xs px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-slate-400 hover:text-white hover:border-purple-400/40 transition-all"
            >
              {ex}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="mt-6 glass-card border-red-500/30 bg-red-500/5 rounded-xl p-4 flex items-center gap-3 text-red-300 text-sm">
          <AlertCircle size={18} /> {error}
        </div>
      )}

      {loading && !result && (
        <div className="mt-8 text-center text-slate-500 text-sm animate-pulse-soft">Detecting entity and relation, querying knowledge base…</div>
      )}

      {result && (
        <div className="mt-8 grid md:grid-cols-5 gap-6 animate-fade-in-up">
          <div className="md:col-span-3 space-y-6">
            {/* Answer */}
            <div className="glass-card rounded-2xl p-6">
              <p className="text-xs font-semibold uppercase tracking-wide text-purple-400 mb-2">Answer</p>
              {result.answer ? (
                <p className="text-2xl font-bold text-white">{result.answer}</p>
              ) : (
                <p className="text-slate-400">
                  No matching record found{result.entity ? ` for "${result.entity}"` : ''} in the knowledge base.
                </p>
              )}
              {result.answer_sentence && (
                <p className="text-slate-400 text-sm mt-2">{result.answer_sentence}</p>
              )}
            </div>

            {/* Knowledge lookup */}
            <div className="glass-card rounded-2xl p-6">
              <p className="text-xs font-semibold uppercase tracking-wide text-fuchsia-400 mb-3">Knowledge Lookup</p>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="bg-white/[0.03] rounded-lg p-3 border border-white/5">
                  <p className="text-xs text-slate-500">Entity</p>
                  <p className="text-white font-medium mt-0.5">{result.entity || '—'}</p>
                </div>
                <div className="bg-white/[0.03] rounded-lg p-3 border border-white/5">
                  <p className="text-xs text-slate-500">Relation</p>
                  <p className="text-white font-medium mt-0.5">{result.relation || '—'}</p>
                </div>
                <div className="bg-white/[0.03] rounded-lg p-3 border border-white/5 col-span-2">
                  <p className="text-xs text-slate-500">Source</p>
                  <p className="text-white font-medium mt-0.5">{result.source}</p>
                </div>
              </div>
            </div>

            {/* Structured result / mini graph */}
            {result.entity && result.relation && result.answer && (
              <div className="glass-card rounded-2xl p-6">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-400 mb-4">Structured Result</p>
                <div className="flex items-center gap-3 flex-wrap">
                  <span className="px-4 py-2 rounded-lg bg-purple-500/15 text-purple-200 font-semibold text-sm border border-purple-400/20">
                    {result.entity}
                  </span>
                  <div className="flex items-center gap-1.5 text-slate-500 text-xs">
                    <Link2 size={13} /> {result.relation}
                    <span className="text-slate-600">──▶</span>
                  </div>
                  <span className="px-4 py-2 rounded-lg bg-fuchsia-500/15 text-fuchsia-200 font-semibold text-sm border border-fuchsia-400/20">
                    {result.answer}
                  </span>
                </div>
                {result.full_record && Object.keys(result.full_record).length > 1 && (
                  <div className="mt-4 pt-4 border-t border-white/10">
                    <p className="text-xs text-slate-500 mb-2">All known relations for {result.entity}:</p>
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(result.full_record).map(([rel, val]) => (
                        <span key={rel} className="text-xs px-2.5 py-1 rounded-full bg-white/5 border border-white/10 text-slate-400">
                          {rel}: <span className="text-slate-200">{val}</span>
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          <div className="md:col-span-2">
            <div className="glass-card rounded-2xl p-6 sticky top-24">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-400 mb-4">Reasoning Pipeline</p>
              <PipelineSteps steps={result.pipeline || []} accent="purple" />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
