import { useState } from 'react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer,
} from 'recharts'

const METRICAS = [
  { key: 'tempo',  label: 'Tempo da query', field: 'duracao_query_segundos', unit: 's',  color: '#26610A' },
  { key: 'linhas', label: 'Linhas',          field: 'total_linhas',           unit: '',   color: '#3182ce' },
  { key: 'saldo',  label: 'Saldo',           field: 'soma_saldo',             unit: '',   color: '#805ad5' },
]

function makeDot(color) {
  return function CustomDot({ cx, cy, payload }) {
    if (!payload) return null
    const isErr = payload.status_consulta !== 'OK'
    return <circle cx={cx} cy={cy} r={isErr ? 6 : 4} fill={isErr ? '#ed8936' : color} stroke="#fff" strokeWidth={isErr ? 2 : 0} />
  }
}

function formatValue(v, key) {
  if (v == null) return '—'
  if (key === 'tempo') return `${v}s`
  if (key === 'saldo') return v.toLocaleString('pt-BR', { minimumFractionDigits: 2 })
  return v.toLocaleString('pt-BR')
}

export default function QueryTimeChart({ historico = [] }) {
  const [metrica, setMetrica] = useState('tempo')
  const m = METRICAS.find(x => x.key === metrica)

  const data = historico.map(h => ({
    data: h.dt_checagem?.slice(0, 10) ?? '',
    valor: h[m.field],
    status_consulta: h.status_consulta,
  }))

  const yWidth = metrica === 'saldo' ? 70 : metrica === 'linhas' ? 50 : 35

  return (
    <div className="panel" style={{ marginBottom: 20 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12, flexWrap: 'wrap', gap: 8 }}>
        <div className="panel-title" style={{ marginBottom: 0 }}>Histórico (30 dias)</div>
        <div style={{ display: 'flex', gap: 6 }}>
          {METRICAS.map(opt => (
            <button
              key={opt.key}
              onClick={() => setMetrica(opt.key)}
              style={{
                padding: '4px 12px', borderRadius: 20, border: 'none', cursor: 'pointer',
                fontSize: 11, fontWeight: 600, transition: 'all 0.15s',
                background: metrica === opt.key ? opt.color : '#f0f4f0',
                color: metrica === opt.key ? '#fff' : '#718096',
              }}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      <ResponsiveContainer width="100%" height={130}>
        <LineChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f4f0" />
          <XAxis dataKey="data" tick={{ fontSize: 10, fill: '#a0aec0' }} tickLine={false} interval="preserveStartEnd" />
          <YAxis tick={{ fontSize: 10, fill: '#a0aec0' }} tickLine={false} unit={m.unit} width={yWidth} />
          <Tooltip
            formatter={(v, _, props) => [
              metrica === 'tempo' && props.payload.status_consulta !== 'OK'
                ? props.payload.status_consulta
                : formatValue(v, metrica),
              m.label,
            ]}
            labelFormatter={l => `Data: ${l}`}
          />
          <Line
            type="monotone"
            dataKey="valor"
            stroke={m.color}
            strokeWidth={2}
            dot={makeDot(m.color)()}
            activeDot={{ r: 6 }}
            connectNulls
          />
        </LineChart>
      </ResponsiveContainer>

      <div style={{ display: 'flex', gap: 14, marginTop: 8, fontSize: 11, color: '#718096' }}>
        <span><span style={{ display: 'inline-block', width: 10, height: 10, borderRadius: 2, background: m.color, marginRight: 4 }} />{m.label}</span>
        <span><span style={{ display: 'inline-block', width: 10, height: 10, borderRadius: 2, background: '#ed8936', marginRight: 4 }} />Timeout/Erro</span>
      </div>
    </div>
  )
}
