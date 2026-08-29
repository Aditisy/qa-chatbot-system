import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import IRQA from './pages/IRQA'
import KnowledgeQA from './pages/KnowledgeQA'
import Chat from './pages/Chat'
import Evaluation from './pages/Evaluation'

export default function App() {
  return (
    <div className="min-h-screen">
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/ir-qa" element={<IRQA />} />
        <Route path="/knowledge-qa" element={<KnowledgeQA />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/evaluation" element={<Evaluation />} />
      </Routes>
    </div>
  )
}
