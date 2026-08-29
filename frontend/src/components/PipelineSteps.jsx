import { CheckCircle2 } from 'lucide-react'

export default function PipelineSteps({ steps = [], accent = 'indigo' }) {
  const gradients = {
    indigo: 'from-indigo-500 to-blue-400',
    purple: 'from-purple-500 to-fuchsia-400',
  }
  const textColors = {
    indigo: 'text-indigo-300',
    purple: 'text-purple-300',
  }
  const grad = gradients[accent] || gradients.indigo
  const txt = textColors[accent] || textColors.indigo

  return (
    <div className="space-y-0">
      {steps.map((s, i) => (
        <div key={i} className="flex gap-3 animate-fade-in-up" style={{ animationDelay: `${i * 70}ms` }}>
          <div className="flex flex-col items-center">
            <div className={`w-7 h-7 rounded-full bg-gradient-to-br ${grad} flex items-center justify-center shrink-0 shadow-lg ring-4 ring-white/5`}>
              <CheckCircle2 size={14} className="text-white" />
            </div>
            {i < steps.length - 1 && (
              <div className={`w-px flex-1 min-h-[24px] bg-gradient-to-b ${grad} opacity-20 my-1`} />
            )}
          </div>
          <div className="pb-5">
            <p className={`text-xs font-bold uppercase tracking-wide ${txt}`}>{s.step}</p>
            <p className="text-sm text-slate-300 mt-1 leading-relaxed">{s.detail}</p>
          </div>
        </div>
      ))}
    </div>
  )
}
