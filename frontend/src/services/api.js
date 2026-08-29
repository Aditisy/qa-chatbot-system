const BASE = '/api'

async function post(path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Request failed')
  }
  return res.json()
}

async function get(path) {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Request failed')
  }
  return res.json()
}

export const api = {
  health: () => get('/health'),
  askIR: (question) => post('/ir/ask', { question }),
  irDocuments: () => get('/ir/documents'),
  askKB: (question) => post('/knowledge/ask', { question }),
  kbEntities: () => get('/knowledge/entities'),
  chat: (message, sessionId) => post('/chat', { message, session_id: sessionId }),
  resetChat: (sessionId) => post('/chat/reset', { session_id: sessionId }),
  evaluation: () => get('/evaluation'),
}
