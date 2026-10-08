import { useState, useRef, useEffect } from 'react'
import { Send, RotateCcw, Bot, User, Loader2 } from 'lucide-react'
import { api } from '../services/api'

const SESSION_ID = sessionStorage.getItem('qa-session') || crypto.randomUUID()
sessionStorage.setItem('qa-session', SESSION_ID)

const STARTER = {
  role: 'assistant',
  text: "Hi! I'm the QA Assistant. Ask me something like \"What are the symptoms of Diabetes?\" — then try a follow-up like \"What is its treatment?\"",
  source: null,
}

export default function Chat() {
  const [messages, setMessages] = useState([STARTER])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const send = async () => {
    const text = input.trim()
    if (!text || loading) return
    setInput('')
    setMessages((m) => [...m, { role: 'user', text }])
    setLoading(true)
    try {
      const data = await api.chat(text, SESSION_ID)
      setMessages((m) => [...m, { role: 'assistant', text: data.response, source: data.source, intent: data.intent }])
    } catch (e) {
      setMessages((m) => [...m, { role: 'assistant', text: `Error: ${e.message}`, source: null }])
    } finally {
      setLoading(false)
    }
  }

  const reset = async () => {
    try {
      await api.resetChat(SESSION_ID)
    } catch {}
    setMessages([STARTER])
  }

  const sourceBadge = (source) => {
    if (!source) return null
    const styles = {
      'Knowledge Base': 'bg-purple-500/15 text-purple-300 border-purple-400/20',
      'Document Retrieval': 'bg-indigo-500/15 text-indigo-300 border-indigo-400/20',
      'Dialogue Manager': 'bg-emerald-500/15 text-emerald-300 border-emerald-400/20',
    }
    return (
      <span className={`text-[10px] px-2 py-0.5 rounded-full border font-medium ${styles[source] || styles['Dialogue Manager']}`}>
        Source: {source}
      </span>
    )
  }

  return (
    <div className="max-w-3xl mx-auto px-6 py-10">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center">
              <Bot size={17} className="text-white" />
            </div>
            QA Assistant
          </h1>
          <p className="text-slate-400 text-sm ml-12 mt-1">Routes each question to Knowledge Base or Document Retrieval automatically</p>
        </div>
        <button
          onClick={reset}
          disabled={loading}
          className="flex items-center gap-1.5 text-xs px-3 py-2 rounded-lg border border-white/10 text-slate-400 hover:text-white hover:bg-white/5 transition-all"
        >
          <RotateCcw size={13} /> Reset
        </button>
      </div>

      <p className="text-xs text-slate-400 mb-4">Educational sample data only; healthcare responses are not medical advice.</p>
      <div className="glass-card rounded-2xl flex flex-col h-[65vh]">
        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          {messages.map((m, i) => (
            <div key={i} className={`flex gap-3 animate-fade-in-up ${m.role === 'user' ? 'flex-row-reverse' : ''}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                m.role === 'user' ? 'bg-white/10' : 'bg-gradient-to-br from-emerald-500 to-teal-500'
              }`}>
                {m.role === 'user' ? <User size={14} className="text-slate-300" /> : <Bot size={14} className="text-white" />}
              </div>
              <div className={`max-w-[75%] ${m.role === 'user' ? 'items-end' : 'items-start'} flex flex-col gap-1`}>
                <div className={`rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                  m.role === 'user'
                    ? 'bg-gradient-to-br from-indigo-500 to-blue-600 text-white rounded-tr-sm'
                    : 'bg-white/[0.06] text-slate-200 border border-white/10 rounded-tl-sm'
                }`}>
                  {m.text}
                </div>
                {m.source && sourceBadge(m.source)}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center shrink-0">
                <Bot size={14} className="text-white" />
              </div>
              <div className="bg-white/[0.06] border border-white/10 rounded-2xl rounded-tl-sm px-4 py-2.5">
                <Loader2 size={14} className="animate-spin text-slate-400" />
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <div className="border-t border-white/10 p-4 flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && send()}
            placeholder="Ask something..."
            className="flex-1 bg-navy-900/70 border border-white/10 rounded-xl px-4 py-2.5 text-white placeholder-slate-600 outline-none focus:border-emerald-400/50 focus:ring-2 focus:ring-emerald-500/20 transition-all text-sm"
          />
          <button
            onClick={send}
            disabled={loading}
            className="px-4 py-2.5 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 text-white font-medium hover:brightness-110 active:scale-95 transition-all disabled:opacity-50 flex items-center gap-1.5"
          >
            <Send size={15} /> Send
          </button>
        </div>
      </div>
    </div>
  )
}
