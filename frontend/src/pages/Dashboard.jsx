import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getBases, sondarTodas } from '../api'
import Header from '../components/Header'
import StatusBadge from '../components/StatusBadge'
import ConsultaBadge from '../components/ConsultaBadge'
import HistoryBar from '../components/HistoryBar'

function SummaryCard({ label, value, color, sub }) {
  return (
    <div style={{
      background: '#fff', borderRadius: 10, padding: '14px 20px',
      flex: 1, minWidth: 130, boxShadow: '0 1px 4px rgba(0,0,0,0.07)',
      borderTop: `3px solid ${color ?? '#e8ede6'}`,
    }}>
      <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.8px', color: '#718096', fontWeight: 600 }}>
        {label}
      </div>
      <div style={{ fontFamily: "'Exo 2', sans-serif", fontSize: 28, fontWeight: 700, color: color ?? '#26610A', marginTop: 4 }}>
        {value}
      </div>
      {sub && <div style={{ fontSize: 11, color: '#a0aec0' }}>{sub}</div>}
    </div>
  )
}

export default function Dashboard() {
  const [bases, setBases] = useState([])
  const [loading, setLoading] = useState(true)
  const [busca, setBusca] = useState('')
  const [sondando, setSondando] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    getBases().then(setBases).finally(() => setLoading(false))
  }, [])

  const handleSondar = async () => {
    setSondando(true)
    await sondarTodas()
    setTimeout(() => { getBases().then(setBases); setSondando(false) }, 2000)
  }

  const filtradas = bases.filter(b => b.nome_base.includes(busca.toLowerCase()))
  const total = bases.length
  const ok = bases.filter(b => b.status === 'OK').length
  const erro = bases.filter(b => b.status === 'ERRO').length
  const semCheck = bases.filter(b => b.status === 'PRIMEIRO_CHECK').length
  const ultimaCheck = bases.length ? bases.reduce((a, b) => a.dt_checagem > b.dt_checagem ? a : b).dt_checagem : null

  return (
    <div style={{ minHeight: '100vh', background: '#F4F6F3' }}>
      <Header subtitle="Saúde das bases">
        <button className="btn-primary" onClick={handleSondar} disabled={sondando}>
          {sondando ? 'Sondando...' : '⟳ Sondar todas'}
        </button>
      </Header>

      <div className="container">
        <div style={{ display: 'flex', gap: 14, marginBottom: 24, flexWrap: 'wrap' }}>
          <SummaryCard label="Total de bases" value={total} />
          <SummaryCard label="OK" value={ok} color="#24CC63" sub="atualizadas" />
          <SummaryCard label="Com erro" value={erro} color="#e53e3e" sub="requerem atenção" />
          <SummaryCard label="Sem checagem" value={semCheck} color="#d69e2e" sub="nunca sondadas" />
          <div style={{
            background: '#fff', borderRadius: 10, padding: '14px 20px',
            flex: 1, minWidth: 180, boxShadow: '0 1px 4px rgba(0,0,0,0.07)',
          }}>
            <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.8px', color: '#718096', fontWeight: 600 }}>
              Última sondagem
            </div>
            <div style={{ fontFamily: "'Exo 2', sans-serif", fontSize: 16, fontWeight: 700, color: '#2d3748', marginTop: 6 }}>
              {ultimaCheck ? new Date(ultimaCheck).toLocaleString('pt-BR') : '—'}
            </div>
          </div>
        </div>

        <div style={{ background: '#fff', borderRadius: 12, boxShadow: '0 1px 4px rgba(0,0,0,0.07)', overflow: 'hidden' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '16px 20px', borderBottom: '1px solid #edf2f7' }}>
            <span style={{ fontFamily: "'Exo 2', sans-serif", fontSize: 15, fontWeight: 700, color: '#26610A' }}>
              Bases monitoradas
            </span>
            <input
              style={{ border: '1px solid #e2e8f0', borderRadius: 8, padding: '6px 12px', fontFamily: 'Nunito, sans-serif', fontSize: 13, outline: 'none' }}
              placeholder="🔍 Filtrar bases..."
              value={busca}
              onChange={e => setBusca(e.target.value)}
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '2fr 100px 100px 120px 120px 140px 1fr 130px', padding: '10px 20px', background: '#f7fafc', borderBottom: '1px solid #edf2f7' }}>
            {['Base', 'Status', 'Consulta', 'Linhas', 'Max Data', 'Última check', 'Histórico (14d)', ''].map(h => (
              <span key={h} style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.7px', color: '#718096', fontWeight: 700 }}>{h}</span>
            ))}
          </div>

          {loading && <div style={{ padding: 24, color: '#a0aec0', textAlign: 'center' }}>Carregando...</div>}

          {filtradas.map(base => (
            <div
              key={base.nome_base}
              style={{
                display: 'grid',
                gridTemplateColumns: '2fr 100px 100px 120px 120px 140px 1fr 130px',
                padding: '12px 20px', borderBottom: '1px solid #f0f4f0', alignItems: 'center',
                background: base.status === 'ERRO' ? '#fff5f5' : 'transparent',
              }}
            >
              <div>
                <div style={{ fontWeight: 700, fontSize: 13, color: '#2d3748' }}>{base.nome_base}</div>
                <div style={{ fontSize: 11, color: '#a0aec0', fontFamily: 'monospace' }}>{base.schema_tabela}</div>
              </div>
              <div><StatusBadge status={base.status} /></div>
              <div><ConsultaBadge status={base.status_consulta} /></div>
              <div style={{ fontSize: 13, color: '#4a5568' }}>{base.total_linhas?.toLocaleString('pt-BR') ?? '—'}</div>
              <div style={{ fontSize: 13, color: '#4a5568' }}>{base.max_data ?? '—'}</div>
              <div style={{ fontSize: 12, color: '#718096' }}>{base.dt_checagem ? new Date(base.dt_checagem).toLocaleString('pt-BR') : '—'}</div>
              <div><HistoryBar historico={[base]} days={14} /></div>
              <div>
                <button className="btn-secondary" onClick={() => navigate(`/base/${base.nome_base}`)}>
                  Ver detalhes →
                </button>
              </div>
            </div>
          ))}
        </div>

        <div style={{ display: 'flex', gap: 14, marginTop: 10, fontSize: 11, color: '#718096' }}>
          {[['#24CC63','OK'],['#e53e3e','Erro'],['#ed8936','Timeout'],['#ecc94b','Incompleto'],['#e2e8f0','Sem dado']].map(([c,l]) => (
            <span key={l} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
              <span style={{ width: 10, height: 10, borderRadius: 2, background: c, display: 'inline-block' }} />
              {l}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}
