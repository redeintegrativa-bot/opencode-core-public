import { INVESTIMENTOS, PATRIMONIO, DESPESAS, getResumoFinanceiro } from '../data.js'

export function renderAnalise() {
  const resumo = getResumoFinanceiro()
  const totalDespesas = DESPESAS.reduce((acc, d) => acc + d.valor, 0)
  const rendaFixa = INVESTIMENTOS.filter(i => i.risco === 'baixo').reduce((acc, i) => acc + i.valor, 0)
  const rendaVariavel = INVESTIMENTOS.filter(i => i.risco === 'medio' || i.risco === 'alto').reduce((acc, i) => acc + i.valor, 0)

  return `
    <div class="page-header">
      <h1 class="page-title">📊 Análise de Investimentos</h1>
      <p class="page-subtitle">Visão estratégica da sua carteira</p>
    </div>

    <div class="card" style="margin-bottom: 20px;">
      <h3 style="font-size: 16px; font-weight: 600; margin-bottom: 16px;"><i class="fas fa-balance-scale" style="color: var(--accent-green);"></i> Análise Risco x Retorno</h3>
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
        <div>
          <h4 style="font-size: 13px; color: var(--text-secondary); margin-bottom: 12px;">Por Classe de Ativo</h4>
          <div class="bar-chart-item">
            <div class="bar-label"><span>Renda Fixa (Caixinha, WBRL, MP, 99)</span><span style="color: var(--accent-cyan);">R$ ${rendaFixa.toLocaleString('pt-BR')}</span></div>
            <div class="bar-track"><div class="bar-fill" style="width: ${((rendaFixa / resumo.patrimonioTotal) * 100).toFixed(0)}%; background: var(--accent-cyan);"></div></div>
          </div>
          <div class="bar-chart-item">
            <div class="bar-label"><span>Renda Variável (Ações+FIIs+Cripto)</span><span style="color: var(--accent-purple);">R$ ${rendaVariavel.toLocaleString('pt-BR')}</span></div>
            <div class="bar-track"><div class="bar-fill" style="width: ${((rendaVariavel / resumo.patrimonioTotal) * 100).toFixed(0)}%; background: var(--accent-purple);"></div></div>
          </div>
        </div>
        <div>
          <h4 style="font-size: 13px; color: var(--text-secondary); margin-bottom: 12px;">Métricas de Saúde</h4>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
            <div style="background: var(--bg-secondary); padding: 12px; border-radius: 8px; text-align: center;">
              <div style="font-size: 11px; color: var(--text-muted);">Fundo Emergência</div>
              <div style="font-size: 20px; font-weight: 700; color: var(--accent-cyan);">${(resumo.patrimonioTotal / totalDespesas).toFixed(0)}x</div>
            </div>
            <div style="background: var(--bg-secondary); padding: 12px; border-radius: 8px; text-align: center;">
              <div style="font-size: 11px; color: var(--text-muted);">Patrimônio Líq.</div>
              <div style="font-size: 20px; font-weight: 700; color: var(--accent-green);">R$ ${resumo.patrimonioTotal.toLocaleString('pt-BR')}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="card" style="margin-bottom: 20px;">
      <h3 style="font-size: 16px; font-weight: 600; margin-bottom: 16px;"><i class="fas fa-chart-pie" style="color: var(--accent-cyan);"></i> Composição da Carteira</h3>
      <div class="chart-grid">
        <div class="card">
          <h4 style="margin-bottom: 16px;">Distribuição por Risco</h4>
          <div class="chart-wrapper" style="height: 250px;">
            <canvas id="patrimonioChart"></canvas>
          </div>
          <div class="pie-legend">
            <div class="legend-item"><div class="legend-color" style="background: var(--accent-cyan);"></div><span>Baixo Risco: R$ ${rendaFixa.toLocaleString('pt-BR')}</span></div>
            <div class="legend-item"><div class="legend-color" style="background: var(--accent-purple);"></div><span>Alto Risco: R$ ${rendaVariavel.toLocaleString('pt-BR')}</span></div>
          </div>
        </div>
        <div class="card">
          <h4 style="margin-bottom: 16px;">Patrimônio vs Despesas</h4>
          <div class="chart-wrapper" style="height: 250px;">
            <canvas id="despesasChart"></canvas>
          </div>
        </div>
      </div>
    </div>

    <div class="card">
      <h3 style="font-size: 16px; font-weight: 600; margin-bottom: 16px;"><i class="fas fa-list" style="color: var(--accent-purple);"></i> Carteira de Ativos</h3>
      <table class="data-table">
        <thead><tr><th>Ativo</th><th>Tipo</th><th>Valor</th><th>Retorno</th><th>Risco</th></tr></thead>
        <tbody>
          ${INVESTIMENTOS.map(inv => `
            <tr>
              <td>${inv.nome}</td>
              <td>${inv.tipo.replace('_', ' ')}</td>
              <td class="${inv.retorno >= 0 ? 'positive' : 'negative'}">R$ ${inv.valor.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</td>
              <td class="${inv.retorno >= 0 ? 'positive' : 'negative'}">${inv.retorno >= 0 ? '+' : ''}${inv.retorno}%</td>
              <td>${inv.risco.toUpperCase()}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `
}
