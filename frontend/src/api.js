import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export async function getBases() {
  const { data } = await api.get('/bases')
  return data
}

export async function getBase(nome) {
  const { data } = await api.get(`/bases/${nome}`)
  return data
}

export async function getHistorico(nome, limit = 30) {
  const { data } = await api.get(`/bases/${nome}/historico`, { params: { limit } })
  return data
}

export async function sondarTodas() {
  const { data } = await api.post('/sondar')
  return data
}

export async function sondarBase(nome) {
  const { data } = await api.post(`/sondar/${nome}`)
  return data
}
