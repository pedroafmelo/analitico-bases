const CONFIG = {
  OK:         { bg: '#dbeafe', color: '#1e40af', label: 'Consulta OK' },
  TIMEOUT:    { bg: '#feebc8', color: '#744210', label: 'Timeout' },
  INCOMPLETE: { bg: '#fef3c7', color: '#92400e', label: 'Incompleto' },
  ERRO:       { bg: '#fed7d7', color: '#742a2a', label: 'Erro ODBC' },
}

export default function ConsultaBadge({ status }) {
  const cfg = CONFIG[status] ?? CONFIG.ERRO
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
