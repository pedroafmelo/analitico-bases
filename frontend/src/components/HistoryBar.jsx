const BLOCK_COLOR = {
  OK:         '#24CC63',
  ERRO:       '#e53e3e',
  TIMEOUT:    '#ed8936',
  INCOMPLETE: '#ecc94b',
  default:    '#e2e8f0',
}

function blockColor(checagem) {
  if (!checagem) return BLOCK_COLOR.default
  if (checagem.status_consulta !== 'OK') return BLOCK_COLOR[checagem.status_consulta] ?? BLOCK_COLOR.default
  return BLOCK_COLOR[checagem.status] ?? BLOCK_COLOR.default
}

export default function HistoryBar({ historico = [], days = 14, height = 22 }) {
  const slots = Array.from({ length: days }, (_, i) => historico[historico.length - days + i] ?? null)

  return (
    <div style={{ display: 'flex', gap: 2, alignItems: 'center' }}>
      {slots.map((h, i) => (
        <div
          key={i}
          title={h ? `${h.dt_checagem?.slice(0, 10)} — ${h.status}` : 'Sem dado'}
          style={{
            width: 13, height, borderRadius: 3, flexShrink: 0,
            background: blockColor(h),
          }}
        />
      ))}
    </div>
  )
}
