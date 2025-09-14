// Simplified Dashboard App.jsx (with env support)
import React, { useEffect, useMemo, useState } from 'react'

const STORAGE_KEYS = {
  apiBase: 'edd_api_base',
  token: 'edd_token',
  email: 'edd_email',
}

function useStoredState(key, initial = '') {
  const [v, setV] = useState(() => localStorage.getItem(key) ?? initial)
  useEffect(() => {
    if (v === undefined || v === null) return
    localStorage.setItem(key, v)
  }, [key, v])
  return [v, setV]
}

function useAuthHeaders(token) {
  return useMemo(() => (token ? { Authorization: `Bearer ${token}` } : {}), [token])
}

export default function App() {
  const DEFAULT_API_BASE = import.meta.env.VITE_API_BASE || ''
  const [apiBase, setApiBase] = useStoredState(STORAGE_KEYS.apiBase, DEFAULT_API_BASE)
  const [token, setToken] = useStoredState(STORAGE_KEYS.token, '')
  const [email, setEmail] = useStoredState(STORAGE_KEYS.email, '')
  const [password, setPassword] = useState('')
  const headers = useAuthHeaders(token)

  async function call(path, opts = {}) {
    if (!apiBase) throw new Error('Set API base first')
    const res = await fetch(`${apiBase}${path}`, {
      ...opts,
      headers: { 'Content-Type': 'application/json', ...headers, ...(opts.headers || {}) }
    })
    if (!res.ok) {
      const text = await res.text()
      throw new Error(`${res.status} ${res.statusText}: ${text}`)
    }
    const ct = res.headers.get('content-type') || ''
    return ct.includes('application/json') ? res.json() : res.text()
  }

  async function doLogin() {
    try {
      const data = await call('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) })
      setToken(data.access_token)
    } catch (e) { alert(e.message) }
  }

  return (
    <div style={{padding:20,fontFamily:'sans-serif',color:'#eee',background:'#111',height:'100vh'}}>
      <h1>EDD Security Dashboard</h1>
      <div style={{marginBottom:10}}>
        <input placeholder='API Base' value={apiBase} onChange={e=>setApiBase(e.target.value)} />
      </div>
      <div style={{marginBottom:10}}>
        <input placeholder='Email' value={email} onChange={e=>setEmail(e.target.value)} />
      </div>
      <div style={{marginBottom:10}}>
        <input type='password' placeholder='Password' value={password} onChange={e=>setPassword(e.target.value)} />
      </div>
      <button onClick={doLogin}>Login</button>
      {token && <div style={{marginTop:10}}>✅ Token cargado</div>}
    </div>
  )
}
