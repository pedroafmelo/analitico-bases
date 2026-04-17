function Delta({ value, isSaldo }) {
  if (value == null || value === '—') return <span style={{ color: '#a0aec0' }}>—</span>
  const numStr = String(value).replace('%', '').replace('▲ +','').replace('▼ -','').replace('▲ ','').replace('▼ ','')
  const pct = parseFloat(numStr)
  const isAlert = isSaldo && !isNaN(pct) && Math.abs(pct) > 20
  return <span style={{ fontSize: 12, fontWeight: 600, color: isAlert ? '#c53030' : '#718096' }}>{value}</span>
}

function TipoBadge({ tipo }) {
  const styles = {
    'numérico': { background: '#faf5ff', color: '#6b46c1' },
    data:       { background: '#ebf8ff', color: '#2b6cb0' },
    texto:      { background: '#ebf8ff', color: '#2b6cb0' },
  }
  const s = styles[tipo] ?? styles.texto
  return (
    <span style={{ ...s, fontSize: 10, padding: '2px 7px', borderRadius: 10, fontWeight: 600 }}>{tipo}</span>
  )
}

export default function ColumnTable({ colunas = [], colunasAnteriores = [] }) {
  const prevMap = Object.fromEntries(colunasAnteriores.map(c => [c.nome_coluna, c]))

  const formatDelta = (atual, anterior, isPercent = false) => {
    if (atual == null || anterior == null) return '—'
    const diff = atual - anterior
    if (diff === 0) return '—'
    const sign = diff > 0 ? '▲ +' : '▼ '
    if (isPercent) return `${sign}${Math.abs(diff).toFixed(1)}%`
    return `${sign}${Math.abs(diff).toLocaleString('pt-BR')}`
  }

  return (
    <div className="panel" style={{ marginBottom: 24 }}>
      <div className="panel-title">Análise por coluna</div>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
        <thead>
          <tr style={{ background: '#f7fafc', borderBottom: '2px solid #f0f4f0' }}>
            {['Coluna','Tipo','Nulos (atual)','% Nulos','Δ Nulos','Soma (atual)','Δ Soma'].map(h => (
              <th key={h} style={{ textAlign: 'left', padding: '8px 12px', fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.7px', color: '#a0aec0', fontWeight: 700 }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {colunas.map(col => {
            const prev = prevMap[col.nome_coluna]
            return (
              <tr key={col.nome_coluna} style={{ borderBottom: '1px solid #f7faf5' }}>
                <td style={{ padding: '10px 12px', fontFamily: 'monospace', fontWeight: 700, fontSize: 12, color: '#2d3748' }}>{col.nome_coluna}</td>
                <td style={{ padding: '10px 12px' }}><TipoBadge tipo={col.tipo_dado} /></td>
                <td style={{ padding: '10px 12px', color: col.total_nulos > 0 ? '#c53030' : '#276749', fontWeight: 600 }}>
                  {col.total_nulos?.toLocaleString('pt-BR') ?? '—'}
                </td>
                <td style={{ padding: '10px 12px', color: '#4a5568' }}>{col.pct_nulos != null ? `${col.pct_nulos.toFixed(2)}%` : '—'}</td>
                <td style={{ padding: '10px 12px' }}>
                  <span style={{ fontSize: 12, fontWeight: 600, color: '#718096' }}>
                    {prev ? formatDelta(col.total_nulos, prev.total_nulos) : '—'}
                  </span>
                </td>
                <td style={{ padding: '10px 12px', color: '#4a5568' }}>
                  {col.tipo_dado === 'numérico' && col.soma_valor != null
                    ? col.soma_valor.toLocaleString('pt-BR', { minimumFractionDigits: 2 })
                    : <span style={{ color: '#a0aec0' }}>—</span>}
                </td>
                <td style={{ padding: '10px 12px' }}>
                  {col.tipo_dado === 'numérico' && prev?.soma_valor != null && col.soma_valor != null
                    ? <Delta
                        value={`${col.soma_valor > prev.soma_valor ? '▲ +' : '▼ '}${Math.abs(((col.soma_valor - prev.soma_valor) / prev.soma_valor) * 100).toFixed(1)}%`}
                        isSaldo
                      />
                    : <span style={{ color: '#a0aec0' }}>—</span>}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
