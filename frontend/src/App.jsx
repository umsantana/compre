import { useEffect, useState, useCallback } from 'react'
import { NavLink, Navigate, Route, Routes } from 'react-router-dom'
import { api } from './api.js'
import Login from './pages/Login.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Leads from './pages/Leads.jsx'
import Clientes from './pages/Clientes.jsx'
import Licencas from './pages/Licencas.jsx'

export default function App() {
  const [admin, setAdmin] = useState(undefined) // undefined = verificando

  const carregar = useCallback(() => api('/auth/me').then(setAdmin).catch(() => setAdmin(null)), [])
  useEffect(() => {
    carregar()
    const sair = () => setAdmin(null)
    window.addEventListener('compre:unauth', sair)
    return () => window.removeEventListener('compre:unauth', sair)
  }, [carregar])

  if (admin === undefined) return <p className="center">Carregando…</p>
  if (!admin) return <Login onLogin={setAdmin} />

  const sair = async () => {
    await api('/auth/logout', { method: 'POST' })
    setAdmin(null)
  }

  return (
    <div className="layout">
      <aside>
        <h1>Compre</h1>
        <nav>
          <NavLink to="/" end>Resumo</NavLink>
          <NavLink to="/leads">Leads</NavLink>
          <NavLink to="/clientes">Clientes</NavLink>
          <NavLink to="/licencas">Licenças</NavLink>
        </nav>
        <div className="user">
          <span>{admin.nome}</span>
          <small>{admin.perfil}</small>
          <button className="link" onClick={sair}>Sair</button>
        </div>
      </aside>
      <main>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/leads" element={<Leads />} />
          <Route path="/clientes" element={<Clientes />} />
          <Route path="/licencas" element={<Licencas />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </main>
    </div>
  )
}
