import { useEffect, useState } from 'react'
import { api } from '../api.js'

const vazio = { nome: '', documento: '', email: '', telefone: '' }

export default function Clientes() {
  const [lista, setLista] = useState(null)
  const [form, setForm] = useState(vazio)
  const [erro, setErro] = useState('')
  const carregar = () => api('/clientes').then(setLista).catch((e) => setErro(e.message))
  useEffect(() => { carregar() }, [])
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value })

  async function salvar(e) {
    e.preventDefault()
    setErro('')
    const body = { ...form, documento: form.documento || null, telefone: form.telefone || null }
    try { await api('/clientes', { method: 'POST', body }); setForm(vazio); carregar() } catch (err) { setErro(err.message) }
  }

  return (
    <>
      <h2>Clientes</h2>
      <form onSubmit={salvar} className="card inline">
        <label>Nome<input value={form.nome} onChange={set('nome')} required /></label>
        <label>CPF/CNPJ<input value={form.documento} onChange={set('documento')} /></label>
        <label>E-mail<input type="email" value={form.email} onChange={set('email')} required /></label>
        <label>Telefone<input value={form.telefone} onChange={set('telefone')} /></label>
        <button>Cadastrar cliente</button>
      </form>
      {erro && <p className="erro" role="alert">{erro}</p>}
      {!lista ? <p className="muted">Carregando…</p> : lista.length === 0 ? <p className="muted">Nenhum cliente cadastrado. Use o formulário acima para criar o primeiro.</p> : (
        <div className="scroll"><table>
          <thead><tr><th>Nome</th><th>Documento</th><th>E-mail</th><th>Telefone</th><th>Status</th></tr></thead>
          <tbody>{lista.map((c) => <tr key={c.id}><td>{c.nome}</td><td>{c.documento || '—'}</td><td>{c.email}</td><td>{c.telefone || '—'}</td><td>{c.status}</td></tr>)}</tbody>
        </table></div>)}
    </>
  )
}
