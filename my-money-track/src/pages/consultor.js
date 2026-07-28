import { gerarInsights, getSugestoesAlocacao } from '../services/consultant-engine.js'
import { calcularAlocacaoAtual, sugerirRealocacao } from '../services/allocator.js'
import { getDicaDoDia } from '../services/news-engine.js'
import { getResumoFinanceiro, INVESTIMENTOS } from '../data.js'

export function renderConsultor() {
  const insights = gerarInsights()
  const alocacaoAtual = calcularAlocacaoAtual()
  const sugestoes = sugerirRealocacao(alocacaoAtual)
  const alocacaoIdeal = getSugestoesAlocacao()
  const dica = getDicaDoDia()
  const resumo = getResumoFinanceiro()

  return `
    <div class="page-header">
      <h1 class="page-title">🧠 Consultor Financeiro</h1>
      <p class="page-subtitle">Análise inteligente da sua vida financeira</p>
    </div>

    <div class="cards-grid" style="margin-bottom: 20px;">
      <div class="card card-highlight">
        <div class="card-label">Patrimônio</div>
        <div class="card-value orange">R$ ${resumo.patrimonioTotal.toLocaleString('pt-BR')}</div>
        <div class="card-sublabel">Total da carteira</div>
      </div>
      <div class="card">
        <div class="card-label">Renda Semanal</div>
        <div class="card-value green">R$ ${resumo.receitaSemanal}</div>
        <div class="card-sublabel">Receitas ativas</div>
      </div>
      <div class="card">
        <div class="card-label">Despesas</div>
        <div class="card-value red">R$ ${resumo.totalDespesas}/mês</div>
        <div class="card-sublabel">Todas as despesas</div>
      </div>
      <div class="card">
        <div class="card-label">Cobertura</div>
        <div class="card-value purple">${(resumo.patrimonioTotal / resumo.totalDespesas).toFixed(0)}x</div>
        <div class="card-sublabel">Meses de emergência</div>
      </div>
    </div>

    <div class="card" style="margin-bottom: 20px;">
      <h3 style="margin-bottom: 16px;"><i class="fas fa-lightbulb" style="color: var(--accent-orange);"></i> ${dica.titulo}</h3>
      <p style="color: var(--text-secondary); line-height: 1.6;">${dica.icone} ${dica.mensagem}</p>
    </div>

    <div class="card" style="margin-bottom: 20px;">
      <h3 style="margin-bottom: 16px;"><i class="fas fa-brain" style="color: var(--accent-purple);"></i> Insights</h3>
      <div id="consultor-insights">
        ${insights.map(i => `
          <div style="padding: 12px; margin-bottom: 8px; background: var(--bg-secondary); border-radius: var(--radius-md); border-left: 3px solid ${
            i.tipo === 'positivo' ? 'var(--accent-green)' :
            i.tipo === 'alerta' ? 'var(--accent-red)' :
            i.tipo === 'dica' ? 'var(--accent-orange)' : 'var(--accent-cyan)'
          };">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
              <span style="font-size: 18px;">${i.icone}</span>
              <span style="font-weight: 600; font-size: 14px;">${i.titulo}</span>
            </div>
            <p style="font-size: 13px; color: var(--text-secondary); line-height: 1.5;">${i.mensagem}</p>
          </div>
        `).join('')}
      </div>
    </div>

    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
      <div class="card">
        <h3 style="margin-bottom: 16px;"><i class="fas fa-chart-pie" style="color: var(--accent-cyan);"></i> Alocação Atual</h3>
        ${alocacaoAtual.map(a => `
          <div class="bar-chart-item">
            <div class="bar-label">
              <span>${a.nome}</span>
              <span style="color: var(--accent-cyan);">${a.pct}%</span>
            </div>
            <div class="bar-track"><div class="bar-fill" style="width: ${a.pct}%; background: var(--accent-cyan);"></div></div>
          </div>
        `).join('')}
      </div>
      <div class="card">
        <h3 style="margin-bottom: 16px;"><i class="fas fa-arrows-alt-h" style="color: var(--accent-green);"></i> Sugestão de Realocação</h3>
        <table class="data-table">
          <thead><tr><th>Classe</th><th>Atual</th><th>Ideal</th><th>Ação</th></tr></thead>
          <tbody>
            ${sugestoes.map(s => `
              <tr>
                <td>${s.classe}</td>
                <td>${s.atual}%</td>
                <td>${s.ideal}%</td>
                <td style="color: ${s.acao === 'OK' ? 'var(--accent-green)' : 'var(--accent-orange)'};">${s.acao}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>

    <div class="card">
      <h3 style="margin-bottom: 16px;"><i class="fas fa-flag-checkered" style="color: var(--accent-purple);"></i> Alocação Ideal</h3>
      <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;">
        ${Object.entries(alocacaoIdeal).map(([key, val]) => `
          <div style="background: var(--bg-secondary); padding: 16px; border-radius: var(--radius-md); text-align: center;">
            <div style="font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">
              ${key.replace(/([A-Z])/g, ' $1').trim()}
            </div>
            <div style="font-size: 24px; font-weight: 700; color: var(--accent-cyan);">${val.pct}%</div>
            <div style="font-size: 11px; color: var(--text-secondary);">R$ ${val.valor.toFixed(0)}</div>
            <div style="font-size: 10px; color: var(--text-muted); margin-top: 4px;">${val.destino}</div>
          </div>
        `).join('')}
      </div>
    </div>
  `
}
