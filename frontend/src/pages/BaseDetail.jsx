import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getBase, getHistorico, sondarBase } from '../api'
import Header from '../components/Header'
import StatusBadge from '../components/StatusBadge'
import ConsultaBadge from '../components/ConsultaBadge'
import HistoryBar from '../components/HistoryBar'
import MetricCard from '../components/MetricCard'
import CoreDistribution from '../components/CoreDistribution'
import QueryTimeChart from '../components/QueryTimeChart'
import ColumnTable from '../components/ColumnTable'

function fmt(n, opts = {}) {
  if (n == null) return '—'
  return typeof n === 'number' ? n.toLocaleString('pt-BR', opts) : n
}

function deltaPct(atual, anterior) {
  if (atual == null || !anterior) return null
  const d = ((atual - anterior) / anterior) * 100
  return `${d >= 0 ? '▲ +' : '▼ '}${Math.abs(d).toFixed(1)}%`
}

export default function BaseDetail() {
  const { nome } = useParams()
  const navigate = useNavigate()
  const [base, setBase] = useState(null)
  const [historico, setHistorico] = useState([])
  const [anterior, setAnterior] = useState(null)
  const [sondando, setSondando] = useState(false)

  useEffect(() => {
    getBase(nome).then(setBase)
    getHistorico(nome, 30).then(hist => {
      setHistorico(hist)
      if (hist.length >= 2) setAnterior(hist[hist.length - 2])
    })
  }, [nome])

  const handleSondar = async () => {
    setSondando(true)
    await sondarBase(nome)
    setTimeout(() => {
      getBase(nome).then(setBase)
      getHistorico(nome, 30).then(hist => { setHistorico(hist); if (hist.length >= 2) setAnterior(hist[hist.length - 2]) })
      setSondando(false)
    }, 3000)
  }

  if (!base) return <div style={{ padding: 40, color: '#a0aec0' }}>Carregando...</div>

  const cobPct = base.total_cobertura_sicredi
    ? ((base.total_cobertura_base / base.total_cobertura_sicredi) * 100).toFixed(1) + '%'
    : null

  const cobPctAnterior = anterior?.total_cobertura_sicredi
    ? ((anterior.total_cobertura_base / anterior.total_cobertura_sicredi) * 100).toFixed(1) + '%'
    : null

  const criterios = [
    { label: 'Linhas', ok: !base.erro_linhas },
    { label: 'Data',   ok: !base.erro_data },
    { label: 'Saldo',  ok: !base.erro_saldo },
  ]

  return (
    <div style={{ minHeight: '100vh', background: '#F4F6F3' }}>
      <Header subtitle="Análise individual">
        <button className="btn-ghost" onClick={() => navigate('/')}>← Voltar</button>
        <button className="btn-primary" onClick={handleSondar} disabled={sondando}>
          {sondando ? 'Sondando...' : '⟳ Sondar esta base'}
        </button>
      </Header>

      <div className="container">

        <div className="panel" style={{ marginBottom: 20 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
                <h2 style={{ fontFamily: "'Exo 2', sans-serif", fontSize: 22, fontWeight: 700, color: '#26610A' }}>{nome}</h2>
                <StatusBadge status={base.status} />
                <ConsultaBadge status={base.status_consulta} />
              </div>
              <span style={{ display: 'inline-block', background: '#f0f4f0', color: '#4a5568', fontSize: 12, padding: '3px 10px', borderRadius: 6, marginTop: 4, fontFamily: 'monospace' }}>
                {base.schema_tabela ?? nome}
              </span>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: 11, color: '#a0aec0', textTransform: 'uppercase', letterSpacing: '0.7px' }}>Última sondagem</div>
              <div style={{ fontSize: 15, fontWeight: 700, color: '#2d3748', marginTop: 2 }}>
                {base.dt_checagem ? new Date(base.dt_checagem).toLocaleString('pt-BR') : '—'}
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: 24, marginTop: 14, flexWrap: 'wrap', borderTop: '1px solid #f0f4f0', paddingTop: 14 }}>
            <div><div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.7px', color: '#a0aec0', fontWeight: 700 }}>Coluna de data</div>
              <div style={{ fontSize: 13, color: '#4a5568', fontWeight: 600, fontFamily: 'monospace' }}>{base.coluna_data ?? '—'}</div></div>
            <div><div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.7px', color: '#a0aec0', fontWeight: 700 }}>Data evolui?</div>
              <div style={{ fontSize: 13, color: '#4a5568', fontWeight: 600 }}>{base.data_evolui != null ? (base.data_evolui ? 'Sim' : 'Não') : '—'}</div></div>
            <div><div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.7px', color: '#a0aec0', fontWeight: 700 }}>Coluna de saldo</div>
              <div style={{ fontSize: 13, color: '#4a5568', fontWeight: 600, fontFamily: 'monospace' }}>{base.coluna_saldo ?? '—'}</div></div>
            <div><div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.7px', color: '#a0aec0', fontWeight: 700 }}>Cobertura por</div>
              <div style={{ fontSize: 13, color: '#4a5568', fontWeight: 600 }}>{base.tipo_cobertura?.toUpperCase() ?? '—'}</div></div>
            <div>
              <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.7px', color: '#a0aec0', fontWeight: 700 }}>Critérios</div>
              <div style={{ display: 'flex', gap: 6, marginTop: 4, flexWrap: 'wrap' }}>
                {criterios.map(c => (
                  <span key={c.label} style={{
                    background: c.ok ? '#c6f6d5' : '#fed7d7',
                    color: c.ok ? '#22543d' : '#742a2a',
                    fontSize: 11, fontWeight: 700, padding: '2px 8px', borderRadius: 10,
                  }}>{c.label} {c.ok ? '✓' : '✗'}</span>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 14, marginBottom: 20 }}>
          <MetricCard label="Total de linhas"
            current={fmt(base.total_linhas)}
            previous={fmt(anterior?.total_linhas)}
            delta={deltaPct(base.total_linhas, anterior?.total_linhas)} />
          <MetricCard label={`Máx. ${base.coluna_data ?? 'data'}`}
            current={base.max_data ?? '—'}
            previous={anterior?.max_data ?? '—'} />
          <MetricCard label={`Soma ${base.coluna_saldo ?? 'saldo'}`}
            current={base.soma_saldo != null ? fmt(base.soma_saldo, { minimumFractionDigits: 2 }) : '—'}
            previous={anterior?.soma_saldo != null ? fmt(anterior.soma_saldo, { minimumFractionDigits: 2 }) : '—'}
            delta={deltaPct(base.soma_saldo, anterior?.soma_saldo)} />
          <MetricCard label="Cobertura"
            current={cobPct ?? '—'}
            previous={cobPctAnterior ?? '—'} />
          <MetricCard label="Tempo da query"
            current={base.duracao_query_segundos != null ? `${base.duracao_query_segundos}s` : '—'}
            previous={anterior?.duracao_query_segundos != null ? `${anterior.duracao_query_segundos}s` : '—'} />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 14, marginBottom: 20 }}>
          <div className="panel">
            <div className="panel-title">Histórico de status (30 dias)</div>
            <HistoryBar historico={historico} days={30} height={28} />
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 5, fontSize: 10, color: '#a0aec0' }}>
              <span>{historico[0]?.dt_checagem?.slice(0, 10) ?? ''}</span>
              <span>{historico[historico.length - 1]?.dt_checagem?.slice(0, 10) ?? ''}</span>
            </div>
            <div style={{ display: 'flex', gap: 12, marginTop: 10, fontSize: 11, color: '#718096', flexWrap: 'wrap' }}>
              {[['#24CC63','OK'],['#e53e3e','Erro'],['#ed8936','Timeout'],['#ecc94b','Incompleto'],['#e2e8f0','Sem dado']].map(([c,l]) => (
                <span key={l}><span style={{ display: 'inline-block', width: 10, height: 10, borderRadius: 2, background: c, marginRight: 3 }} />{l}</span>
              ))}
            </div>
          </div>
          <CoreDistribution
            pctSicredi={base.pct_sicredi}
            pctFisital={base.pct_fisital}
            pctWoop={base.pct_woop}
            coberturaBase={base.total_cobertura_base}
            coberturaSicredi={base.total_cobertura_sicredi}
          />
        </div>

        <QueryTimeChart historico={historico} />

        <ColumnTable
          colunas={base.metricas_colunas ?? []}
          colunasAnteriores={anterior ? [] : []}
        />

      </div>
    </div>
  )
}
