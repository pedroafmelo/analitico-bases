import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer,
} from 'recharts'

function CustomDot({ cx, cy, payload }) {
  if (!payload) return null
  const color = payload.status_consulta !== 'OK' ? '#ed8936' : '#26610A'
  const r = payload.status_consulta !== 'OK' ? 6 : 4
  return <circle cx={cx} cy={cy} r={r} fill={color} stroke="#fff" strokeWidth={payload.status_consulta !== 'OK' ? 2 : 0} />
}

export default function QueryTimeChart({ historico = [] }) {
  const data = historico.map(h => ({
    data: h.dt_checagem?.slice(0, 10) ?? '',
    tempo: h.duracao_query_segundos,
    status_consulta: h.status_consulta,
  }))

  return (
    <div className="panel" style={{ marginBottom: 20 }}>
      <div className="panel-title">Histórico de tempo da query (30 dias)</div>
      <div style={{ fontSize: 12, color: '#a0aec0', marginBottom: 12 }}>
        Segundos por execução — pontos laranja indicam timeout/erro
      </div>
      <ResponsiveContainer width="100%" height={120}>
        <LineChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f4f0" />
          <XAxis dataKey="data" tick={{ fontSize: 10, fill: '#a0aec0' }} tickLine={false} interval="preserveStartEnd" />
          <YAxis tick={{ fontSize: 10, fill: '#a0aec0' }} tickLine={false} unit="s" width={35} />
          <Tooltip
            formatter={(v, _, props) => [
              props.payload.status_consulta !== 'OK' ? props.payload.status_consulta : `${v}s`,
              'Tempo'
            ]}
            labelFormatter={l => `Data: ${l}`}
          />
          <Line
            type="monotone"
            dataKey="tempo"
            stroke="#26610A"
            strokeWidth={2}
            dot={<CustomDot />}
            activeDot={{ r: 6 }}
            connectNulls
          />
        </LineChart>
      </ResponsiveContainer>
      <div style={{ display: 'flex', gap: 14, marginTop: 8, fontSize: 11, color: '#718096' }}>
        <span><span style={{ display: 'inline-block', width: 10, height: 10, borderRadius: 2, background: '#26610A', marginRight: 4 }} />Tempo (s)</span>
        <span><span style={{ display: 'inline-block', width: 10, height: 10, borderRadius: 2, background: '#ed8936', marginRight: 4 }} />Timeout/Erro</span>
      </div>
    </div>
  )
}
