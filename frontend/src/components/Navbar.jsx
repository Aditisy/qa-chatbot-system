import { NavLink } from 'react-router-dom'
import { Brain, Search, Database, MessageSquare, BarChart3, Circle } from 'lucide-react'

const links = [
  { to: '/', label: 'Home', icon: Brain, end: true },
  { to: '/ir-qa', label: 'IR-Based QA', icon: Search },
  { to: '/knowledge-qa', label: 'Knowledge-Based QA', icon: Database },
  { to: '/chat', label: 'Chat', icon: MessageSquare },
  { to: '/evaluation', label: 'Evaluation', icon: BarChart3 },
]

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 border-b border-white/10 bg-navy-950/70 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <NavLink to="/" className="flex items-center gap-2.5 group shrink-0">
          <div className="relative w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 via-purple-500 to-fuchsia-500 flex items-center justify-center shadow-glow group-hover:scale-105 group-hover:rotate-3 transition-all duration-300">
            <Brain size={18} className="text-white" />
          </div>
          <span className="font-bold text-white tracking-tight text-[15px]">
            Intelligent QA <span className="text-slate-500 font-medium">System</span>
          </span>
        </NavLink>

        <nav className="hidden md:flex items-center gap-1">
          {links.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                `relative flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? 'text-white'
                    : 'text-slate-400 hover:text-white hover:bg-white/5'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  {isActive && (
                    <span className="absolute inset-0 rounded-lg bg-gradient-to-r from-indigo-500/20 to-purple-500/20 border border-indigo-400/30" />
                  )}
                  <Icon size={15} className="relative" />
                  <span className="relative">{label}</span>
                </>
              )}
            </NavLink>
          ))}
        </nav>

        <div className="hidden sm:flex items-center gap-1.5 text-xs text-slate-500 shrink-0">
          <Circle size={7} className="fill-emerald-400 text-emerald-400 animate-pulse-soft" />
          System Online
        </div>
      </div>
    </header>
  )
}
