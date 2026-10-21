const BASE = import.meta.env.VITE_API_URL || ''

function mensagem(detail) {
  if (Array.isArray(detail)) return detail[0]?.msg?.replace('Value error, ', '') || 'Dados inválidos.'
  return detail || 'Algo deu errado. Tente novamente.'
}

export async function api(path, { method = 'GET', body } = {}) {
  const res = await fetch(`${BASE}/api${path}`, {
    method,
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'compre' },
    body: body ? JSON.stringify(body) : undefined,
  })
  if (res.status === 401 && !path.startsWith('/auth/')) window.dispatchEvent(new Event('compre:unauth'))
  const data = res.status === 204 ? null : await res.json().catch(() => null)
  if (!res.ok) throw new Error(mensagem(data?.detail))
  return data
}
