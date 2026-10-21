import { useEffect, useState } from 'react'
import { api } from '../api.js'

export default function Licencas() {
  const [lics, setLics] = useState(null)
  const [clientes, setClientes] = useState([])
  const [produtos, setProdutos] = useState([])
  const [form, setForm] = useState({ cliente_id: '', produto_id: '', status: 'trial', fim: '', limite_usuarios: '' })
  const [chave, setChave] = useState('')
  const [erro, setErro] = useState('')

  const carregar = () => api('/licencas').then(setLics).catch((e) => setErro(e.message))
  useEffect(() => {
    carregar()
    api('/clientes').then(setClientes).catch(() => {})
    api('/produtos').then(setProdutos).catch(() => {})
  }, [])
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value })
  const nomeCliente = (id) => clientes.find((c) => c.id === id)?.nome || `#${id}`
  const nomeProduto = (id) => produtos.find((p) => p.id === id)?.nome || `#${id}`

  async function criar(e) {
    e.preventDefault()
    setErro('')
    setChave('')
    const body = {
      cliente_id: Number(form.cliente_id), produto_id: Number(form.produto_id), status: form.status,
      fim: form.fim || null, limite_usuarios: form.limite_usuarios ? Number(form.limite_usuarios) : null,
    }
    try { const r = await api('/licencas', { method: 'POST', body }); setChave(r.chave); carregar() } catch (err) { setErro(err.message) }
  }
  async function status(id, s) {
    try { await api(`/licencas/${id}/status`, { method: 'PATCH', body: { status: s } }); carregar() } catch (err) { setErro(err.message) }
  }

  return (
    <>
      <h2>Licenças</h2>
      <form onSubmit={criar} className="card inline">
        <label>Cliente<select value={form.cliente_id} onChange={set('cliente_id')} required><option value="">Selecione</option>{clientes.map((c) => <option key={c.id} value={c.id}>{c.nome}</option>)}</select></label>
        <label>Sistema<select value={form.produto_id} onChange={set('produto_id')} required><option value="">Selecione</option>{produtos.map((p) => <option key={p.id} value={p.id}>{p.nome}</option>)}</select></label>
        <label>Situação<select value={form.status} onChange={set('status')}><option value="trial">Teste</option><option value="ativa">Ativa</option></select></label>
        <label>Válida até<input type="date" value={form.fim} onChange={set('fim')} /></label>
        <label>Limite de usuários<input type="number" min="1" value={form.limite_usuarios} onChange={set('limite_usuarios')} /></label>
        <button>Criar licença</button>
      </form>
      {chave && <div className="card chave" role="status"><b>Chave da licença (aparece só agora):</b><code>{chave}</code><button className="link" onClick={() => navigator.clipboard.writeText(chave)}>Copiar</button></div>}
      {erro && <p className="erro" role="alert">{erro}</p>}
      {!lics ? <p className="muted">Carregando…</p> : lics.length === 0 ? <p className="muted">Nenhuma licença criada. Cadastre um cliente e crie a primeira licença acima.</p> : (
        <div className="scroll"><table>
          <thead><tr><th>Cliente</th><th>Sistema</th><th>Situação</th><th>Válida até</th><th>Usuários</th><th>Ações</th></tr></thead>
          <tbody>{lics.map((l) => (
            <tr key={l.id}>
              <td>{nomeCliente(l.cliente_id)}</td><td>{nomeProduto(l.produto_id)}</td>
              <td><span className={`tag ${l.status}`}>{l.status}</span></td>
              <td>{l.fim ? new Date(l.fim + 'T00:00').toLocaleDateString('pt-BR') : 'sem prazo'}</td>
              <td>{l.limite_usuarios || '—'}</td>
              <td className="acoes">
                {l.status !== 'ativa' && <button className="link" onClick={() => status(l.id, 'ativa')}>Ativar</button>}
                {l.status !== 'suspensa' && <button className="link" onClick={() => status(l.id, 'suspensa')}>Suspender</button>}
                {l.status !== 'cancelada' && <button className="link perigo" onClick={() => confirm('Cancelar esta licença?') && status(l.id, 'cancelada')}>Cancelar</button>}
              </td>
            </tr>))}</tbody>
        </table></div>)}
    </>
  )
}
