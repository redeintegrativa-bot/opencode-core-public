import { INVESTIMENTOS, DESPESAS, getResumoFinanceiro } from '../data.js'

export function renderProjecoes() {
  const resumo = getResumoFinanceiro()
  const totalDespesas = DESPESAS.reduce((acc, d) => acc + d.valor, 0)
  const valorTotalInvestido = INVESTIMENTOS.reduce((acc, inv) => acc + inv.valor, 0)

  return `
    <div class="page-header">
      <h1 class="page-title">Projeções</h1>
      <p class="page-subtitle">Crescimento do patrimônio</p>
    </div>

    <div class="cards-grid">
      <div class="card card-highlight">
        <div class="card-label">Patrimônio</div>
        <div class="card-value orange">R$ ${resumo.patrimonioTotal.toLocaleString('pt-BR')}</div>
        <div class="card-sublabel">Valor atual da carteira</div>
      </div>
      <div class="card">
        <div class="card-label">Investido</div>
        <div class="card-value green">R$ ${valorTotalInvestido.toLocaleString('pt-BR')}</div>
        <div class="card-sublabel">Total em ativos</div>
      </div>
      <div class="card">
        <div class="card-label">Despesas</div>
        <div class="card-value red">R$ ${totalDespesas}/mês</div>
        <div class="card-sublabel">Cobertura: ${(resumo.patrimonioTotal / totalDespesas).toFixed(0)} meses</div>
      </div>
      <div class="card">
        <div class="card-label">Ativos</div>
        <div class="card-value cyan">${INVESTIMENTOS.length}</div>
        <div class="card-sublabel">Itens na carteira</div>
      </div>
    </div>
  `
}
