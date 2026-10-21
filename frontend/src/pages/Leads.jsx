import { useEffect, useState } from 'react'
import { api } from '../api.js'

const STATUS = ['novo', 'contato', 'trial', 'cliente', 'perdido']

export default function Leads() {
  const [leads, setLeads] = useState(null)
  const [erro, setErro] = useState('')
  const carregar = () => api('/leads').then(setLeads).catch((e) => setErro(e.message))
  useEffect(() => { carregar() }, [])

  async function mudar(id, status) {
    try { await api(`/leads/${id}`, { method: 'PATCH', body: { status } }); carregar() } catch (e) { setErro(e.message) }
  }

  if (!leads) return <p className="muted">{erro || 'Carregando…'}</p>
  return (
    <>
      <h2>Leads</h2>
      {erro && <p className="erro">{erro}</p>}
      {leads.length === 0 ? <p className="muted">Nenhum lead ainda. Eles chegam pelo formulário da landpage.</p> : (
        <div className="scroll"><table>
          <thead><tr><th>Data</th><th>Nome</th><th>Contato</th><th>Interesse</th><th>Origem</th><th>Status</th></tr></thead>
          <tbody>{leads.map((l) => (
            <tr key={l.id}>
              <td>{new Date(l.criado_em + 'Z').toLocaleDateString('pt-BR')}</td>
              <td>{l.nome}<br /><small>{l.empresa}</small></td>
              <td>{l.email}<br /><small>{l.telefone}</small></td>
              <td>{l.produto_interesse || '—'}</td>
              <td>{l.utm_source || 'direto'}</td>
              <td><select value={l.status} onChange={(e) => mudar(l.id, e.target.value)}>{STATUS.map((s) => <option key={s}>{s}</option>)}</select></td>
            </tr>))}</tbody>
        </table></div>)}
    </>
  )
}
