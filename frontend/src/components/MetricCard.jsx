export default function MetricCard({ label, current, previous, delta, deltaAlert = false, topColor = '#24CC63' }) {
  const showDelta = delta !== null && delta !== undefined

  return (
    <div style={{
      background: '#fff', borderRadius: 10, padding: '16px 20px',
      boxShadow: '0 1px 4px rgba(0,0,0,0.07)',
      borderTop: `3px solid ${topColor}`,
    }}>
      <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.7px', color: '#a0aec0', fontWeight: 700 }}>
        {label}
      </div>
      <div style={{ fontFamily: "'Exo 2', sans-serif", fontSize: 22, fontWeight: 700, color: '#26610A', marginTop: 6 }}>
        {current ?? '—'}
      </div>
      {previous !== undefined && (
        <div style={{ fontSize: 12, color: '#a0aec0', marginTop: 4 }}>
          Anterior: <span style={{ color: '#718096', fontWeight: 600 }}>{previous ?? '—'}</span>
        </div>
      )}
      {showDelta && (
        <div style={{
          fontSize: 12, marginTop: 4, fontWeight: 600,
          color: deltaAlert ? '#c53030' : '#718096',
        }}>
          {delta}
        </div>
      )}
    </div>
  )
}
