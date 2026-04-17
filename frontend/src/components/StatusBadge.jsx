const CONFIG = {
  OK:             { bg: '#c6f6d5', color: '#22543d', label: 'OK' },
  ERRO:           { bg: '#fed7d7', color: '#742a2a', label: 'ERRO' },
  PRIMEIRO_CHECK: { bg: '#fef3c7', color: '#92400e', label: 'NOVO' },
}

export default function StatusBadge({ status }) {
  const cfg = CONFIG[status] ?? CONFIG.PRIMEIRO_CHECK
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 5,
      padding: '4px 12px', borderRadius: 20,
      background: cfg.bg, color: cfg.color,
      fontSize: 12, fontWeight: 700,
    }}>
      <span style={{ width: 7, height: 7, borderRadius: '50%', background: 'currentColor' }} />
      {cfg.label}
    </span>
  )
}
