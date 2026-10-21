import { useEffect, useState } from 'react'
import { api } from '../api.js'

const soma = (o = {}) => Object.values(o).reduce((a, b) => a + b, 0)

export default function Dashboard() {
  const [d, setD] = useState(null)
  const [erro, setErro] = useState('')
  useEffect(() => { api('/dashboard').then(setD).catch((e) => setErro(e.message)) }, [])
  if (erro) return <p className="erro">{erro}</p>
  if (!d) return <p className="muted">Carregando…</p>
  const lic = d.licencas_por_status, leads = d.leads_por_status
  return (
    <>
      <h2>Resumo</h2>
      <div className="grid">
        <div className="card"><b>{d.clientes_ativos}</b><span>clientes ativos</span></div>
        <div className="card"><b>{(lic.ativa || 0) + (lic.trial || 0)}</b><span>licenças em uso ({lic.trial || 0} em teste)</span></div>
        <div className="card"><b>{(lic.inadimplente || 0) + (lic.suspensa || 0)}</b><span>inadimplentes ou suspensas</span></div>
        <div className="card"><b>{leads.novo || 0}</b><span>leads novos (de {soma(leads)} no total)</span></div>
      </div>
    </>
  )
}
