export default function CoreDistribution({ pctSicredi, pctFisital, pctWoop, coberturaBase, coberturaSicredi }) {
  if (pctSicredi == null) return (
    <div className="panel">
      <div className="panel-title">Distribuição de core</div>
      <p style={{ color: '#a0aec0', fontSize: 13 }}>Sem coluna de cobertura configurada</p>
    </div>
  )

  const items = [
    { label: 'SICREDI', pct: pctSicredi, color: '#26610A' },
    { label: 'FISITAL', pct: pctFisital, color: '#24CC63' },
    { label: 'WOOP',    pct: pctWoop,    color: '#90cdf4' },
  ]

  const pctCobertura = coberturaSicredi ? ((coberturaBase / coberturaSicredi) * 100).toFixed(1) : null

  return (
    <div className="panel">
      <div className="panel-title">Distribuição de core</div>

      <div style={{ display: 'flex', height: 24, borderRadius: 6, overflow: 'hidden', marginBottom: 10 }}>
        {items.map(i => (
          <div key={i.label} style={{ background: i.color, width: `${(i.pct ?? 0) * 100}%` }} />
        ))}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {items.map(i => (
          <div key={i.label} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={{ width: 12, height: 12, borderRadius: 3, background: i.color }} />
              <span style={{ color: '#4a5568' }}>{i.label}</span>
            </div>
            <span style={{ fontWeight: 700, color: '#2d3748' }}>
              {i.pct != null ? `${(i.pct * 100).toFixed(1)}%` : '—'}
            </span>
          </div>
        ))}
      </div>

      {pctCobertura && (
        <div style={{ marginTop: 14, paddingTop: 12, borderTop: '1px solid #f0f4f0' }}>
          <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.7px', color: '#a0aec0', fontWeight: 700 }}>
            Cobertura na Sicredi
          </div>
          <div style={{ background: '#e2e8f0', borderRadius: 8, height: 10, marginTop: 8, overflow: 'hidden' }}>
            <div style={{ background: '#24CC63', height: '100%', width: `${pctCobertura}%`, borderRadius: 8 }} />
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 5, fontSize: 12, color: '#718096' }}>
            <span>Distintos: <strong>{coberturaBase?.toLocaleString('pt-BR')}</strong></span>
            <span><strong>{pctCobertura}%</strong> do total</span>
          </div>
        </div>
      )}
    </div>
  )
}
