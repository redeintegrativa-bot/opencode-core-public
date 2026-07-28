import { INVESTIMENTOS, getResumoFinanceiro } from '../data.js'

export function renderDashboard() {
  const resumo = getResumoFinanceiro()

  return `
    <div class="page-header">
      <h1 class="page-title">Resumo</h1>
      <p class="page-subtitle">Visão geral das suas finanças</p>
    </div>

    <div class="cards-grid">
      <div class="card card-highlight">
        <div class="card-label">Patrimônio Total</div>
        <div class="card-value orange">R$ ${resumo.patrimonioTotal.toLocaleString('pt-BR')}</div>
        <div class="card-sublabel">Carteira + Investimentos</div>
      </div>
      <div class="card">
        <div class="card-label">Renda Semanal</div>
        <div class="card-value green">R$ ${resumo.receitaSemanal}</div>
        <div class="card-sublabel">Receitas ativas</div>
      </div>
      <div class="card">
        <div class="card-label">Despesas Mensais</div>
        <div class="card-value red">R$ ${resumo.totalDespesas}</div>
        <div class="card-sublabel">Todas as despesas</div>
      </div>
      <div class="card">
        <div class="card-label">Cobertura</div>
        <div class="card-value purple">${(resumo.patrimonioTotal / resumo.totalDespesas).toFixed(0)}x</div>
        <div class="card-sublabel">Meses de emergência</div>
      </div>
    </div>

    <div class="card" style="margin-top: 20px;">
      <h4 style="margin-bottom: 16px;">Carteira de Ativos</h4>
      <table class="data-table">
        <thead><tr><th>Ativo</th><th>Valor</th></tr></thead>
        <tbody>
          ${INVESTIMENTOS.map(inv => `
            <tr>
              <td>${inv.nome}</td>
              <td class="${inv.retorno >= 0 ? 'positive' : 'negative'}">R$ ${inv.valor.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `
}
