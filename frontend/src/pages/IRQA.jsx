import { useState } from 'react'
import { Search, Loader2, AlertCircle, RotateCcw, FileText, Gauge } from 'lucide-react'
import { api } from '../services/api'
import PipelineSteps from '../components/PipelineSteps'

const EXAMPLES = [
  'Who developed the theory of relativity?',
  'Who formulated the law of universal gravitation?',
  'When did World War II begin?',
  'Who created Python?',
  'When was the Eiffel Tower completed?',
]

export default function IRQA() {
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
      const data = await api.askIR(query)
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
        <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-indigo-500 to-blue-500 flex items-center justify-center">
          <Search size={17} className="text-white" />
        </div>
        <h1 className="text-2xl font-bold text-white">IR-Based QA</h1>
      </div>
      <p className="text-slate-400 text-sm ml-12">
        Question → Retrieved Passages → Extracted Answer → Evidence
      </p>

      {/* Search box */}
      <div className="glass-card rounded-2xl p-6 mt-8">
        <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">Ask a question</label>
        <div className="mt-2 flex gap-3">
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && ask()}
            placeholder="e.g. Who developed the theory of relativity?"
            className="flex-1 bg-navy-900/70 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-slate-600 outline-none focus:border-indigo-400/50 focus:ring-2 focus:ring-indigo-500/20 focus:bg-navy-900 transition-all"
          />
          <button
            onClick={() => ask()}
            disabled={loading}
            className="px-5 py-3 rounded-xl bg-gradient-to-br from-indigo-500 to-blue-600 text-white font-medium hover:brightness-110 hover:shadow-glow active:scale-95 transition-all duration-200 disabled:opacity-50 flex items-center gap-2 shrink-0"
          >
            {loading ? <Loader2 size={16} className="animate-spin" /> : <Search size={16} />}
            Ask Question
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
              className="text-xs px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-slate-400 hover:text-white hover:border-indigo-400/40 transition-all"
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
        <div className="mt-8 text-center text-slate-500 text-sm animate-pulse-soft">Retrieving passages and extracting answer…</div>
      )}

      {result && (
        <div className="mt-8 grid md:grid-cols-5 gap-6 animate-fade-in-up">
          <div className="md:col-span-3 space-y-6">
            {/* Answer card */}
            <div className="glass-card rounded-2xl p-6">
              <p className="text-xs font-semibold uppercase tracking-wide text-indigo-400 mb-2">Answer</p>
              {result.answer ? (
                <>
                  <p className="text-2xl font-bold text-white">{result.answer}</p>
                  <div className="mt-3 flex items-center gap-2">
                    <Gauge size={14} className="text-slate-500" />
                    <div className="flex-1 h-1.5 bg-white/10 rounded-full overflow-hidden max-w-[160px]">
                      <div
                        className="h-full bg-gradient-to-r from-indigo-500 to-blue-400 rounded-full"
                        style={{ width: `${Math.round((result.confidence || 0) * 100)}%` }}
                      />
                    </div>
                    <span className="text-xs text-slate-400">Confidence: {Math.round((result.confidence || 0) * 100)}%</span>
                  </div>
                  {result.source_document && (
                    <p className="text-xs text-slate-500 mt-2">Source document: {result.source_document}</p>
                  )}
                </>
              ) : (
                <p className="text-slate-400">No confident answer could be extracted from the corpus.</p>
              )}
            </div>

            {/* Evidence */}
            {result.evidence && (
              <div className="glass-card rounded-2xl p-6">
                <p className="text-xs font-semibold uppercase tracking-wide text-blue-400 mb-2">Supporting Evidence</p>
                <p className="text-slate-300 leading-relaxed italic">"{result.evidence}"</p>
              </div>
            )}

            {/* Retrieved passages */}
            {result.retrieved_documents?.length > 0 && (
              <div className="glass-card rounded-2xl p-6">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-400 mb-4 flex items-center gap-2">
                  <FileText size={13} /> Retrieved Passages
                </p>
                <div className="space-y-3">
                  {result.retrieved_documents.map((doc, i) => (
                    <div key={doc.doc_id} className="border border-white/10 rounded-xl p-4 bg-white/[0.02]">
                      <div className="flex items-center justify-between mb-1.5">
                        <span className="text-sm font-semibold text-white">Document {i + 1}: {doc.doc_title}</span>
                        <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-500/15 text-indigo-300">
                          Score: {doc.score}
                        </span>
                      </div>
                      <p className="text-xs text-slate-500 line-clamp-3">{doc.text}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Pipeline */}
          <div className="md:col-span-2">
            <div className="glass-card rounded-2xl p-6 sticky top-24">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-400 mb-4">Processing Pipeline</p>
              <PipelineSteps steps={result.pipeline || []} accent="indigo" />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
