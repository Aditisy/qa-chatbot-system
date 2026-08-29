import { useEffect, useState } from 'react'
import { BarChart3, Loader2, AlertCircle, CheckCircle2, XCircle } from 'lucide-react'
import { api } from '../services/api'

function MetricCard({ label, value, color }) {
  const colors = {
    indigo: 'from-indigo-500 to-blue-500 text-indigo-300',
    purple: 'from-purple-500 to-fuchsia-500 text-purple-300',
    emerald: 'from-emerald-500 to-teal-500 text-emerald-300',
  }
  const c = colors[color] || colors.indigo
  return (
    <div className="glass-card rounded-xl p-5">
      <p className="text-xs text-slate-500 font-medium">{label}</p>
      <p className={`text-3xl font-extrabold mt-1 bg-gradient-to-r ${c.split(' ')[0]} ${c.split(' ')[1]} bg-clip-text text-transparent`}>
        {(value * 100).toFixed(1)}%
      </p>
      <div className="mt-2 h-1.5 bg-white/10 rounded-full overflow-hidden">
        <div className={`h-full bg-gradient-to-r ${c.split(' ')[0]} ${c.split(' ')[1]} rounded-full`} style={{ width: `${value * 100}%` }} />
      </div>
    </div>
  )
}

function ResultsTable({ rows, columns }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-xs text-slate-500 uppercase tracking-wide border-b border-white/10">
            {columns.map((c) => <th key={c} className="pb-2 pr-4 font-semibold">{c}</th>)}
            <th className="pb-2">Correct?</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i} className="border-b border-white/5 hover:bg-white/[0.02]">
              {columns.map((c) => {
                const key = c.toLowerCase().replace(/ /g, '_')
                return <td key={c} className="py-2.5 pr-4 text-slate-300 max-w-xs">{String(r[key] ?? '')}</td>
              })}
              <td className="py-2.5">
                {r.correct
                  ? <CheckCircle2 size={16} className="text-emerald-400" />
                  : <XCircle size={16} className="text-red-400" />}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default function Evaluation() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [tab, setTab] = useState('ir')

  useEffect(() => {
    api.evaluation().then(setData).catch((e) => setError(e.message))
  }, [])

  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-6 py-16 text-center">
        <AlertCircle className="mx-auto text-red-400 mb-3" />
        <p className="text-red-300">{error}</p>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="max-w-4xl mx-auto px-6 py-24 text-center text-slate-500">
        <Loader2 className="animate-spin mx-auto mb-3" /> Loading evaluation results…
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto px-6 py-10">
      <div className="flex items-center gap-3 mb-1">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-amber-500 to-orange-500 flex items-center justify-center">
          <BarChart3 size={17} className="text-white" />
        </div>
        <h1 className="text-2xl font-bold text-white">Evaluation</h1>
      </div>
      <p className="text-slate-400 text-sm ml-12">
        Metrics computed live by running the system against the local evaluation dataset — not hardcoded.
      </p>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-8">
        <MetricCard label="IR Exact Match" value={data.ir.exact_match} color="indigo" />
        <MetricCard label="IR F1 Score" value={data.ir.f1} color="indigo" />
        <MetricCard label="KB Accuracy" value={data.kb.accuracy} color="purple" />
        <MetricCard label="Dialogue Intent Accuracy" value={data.dialogue.intent_accuracy} color="emerald" />
      </div>

      <div className="glass-card rounded-2xl mt-8 overflow-hidden">
        <div className="flex border-b border-white/10">
          {[
            { id: 'ir', label: `IR-Based QA (${data.ir.total})` },
            { id: 'kb', label: `Knowledge-Based QA (${data.kb.total})` },
            { id: 'dialogue', label: `Dialogue (${data.dialogue.total})` },
          ].map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`px-5 py-3 text-sm font-medium transition-all ${
                tab === t.id ? 'text-white border-b-2 border-indigo-400' : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
        <div className="p-6">
          {tab === 'ir' && <ResultsTable rows={data.ir.rows} columns={['Question', 'Expected Answer', 'System Answer']} />}
          {tab === 'kb' && <ResultsTable rows={data.kb.rows} columns={['Question', 'Expected Answer', 'System Answer']} />}
          {tab === 'dialogue' && (
            <ResultsTable
              rows={data.dialogue.rows.map((r) => ({ ...r, expected_intent: r.expected_intent, predicted_intent: r.predicted_intent, user: r.user }))}
              columns={['User', 'Expected Intent', 'Predicted Intent', 'Response']}
            />
          )}
        </div>
      </div>

      <p className="text-xs text-slate-600 mt-4 text-center">
        Known limitations are documented in the project README's "Analysis &amp; Interpretation" section.
      </p>
    </div>
  )
}
