import { PATRIMONIO, DESPESAS, getResumoFinanceiro } from '../data.js'

export function renderMovimentos() {
  const resumo = getResumoFinanceiro()

  return `
    <div class="page-header">
      <h1 class="page-title">🔄 Fluxo de Caixa</h1>
      <p class="page-subtitle">Resumo financeiro</p>
    </div>

    <div class="card">
      <h3 style="margin-bottom: 12px;"><i class="fas fa-exchange-alt"></i> Fluxo de Caixa</h3>
      <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px;">
        <div style="background: var(--bg-secondary); padding: 12px; border-radius: 8px;">
          <div style="color: var(--text-muted); font-size: 11px;">Renda Semanal</div>
          <div style="color: var(--accent-green); font-size: 20px; font-weight: 700;">R$ ${resumo.receitaSemanal}</div>
        </div>
        <div style="background: var(--bg-secondary); padding: 12px; border-radius: 8px;">
          <div style="color: var(--text-muted); font-size: 11px;">Despesas</div>
          <div style="color: var(--accent-red); font-size: 20px; font-weight: 700;">R$ ${resumo.totalDespesas}/mês</div>
        </div>
        <div style="background: var(--bg-secondary); padding: 12px; border-radius: 8px;">
          <div style="color: var(--text-muted); font-size: 11px;">Patrimônio</div>
          <div style="color: var(--accent-green); font-size: 20px; font-weight: 700;">R$ ${PATRIMONIO.total.toLocaleString('pt-BR')}</div>
        </div>
      </div>
      <div style="margin-top: 12px; padding: 12px; background: var(--bg-tertiary); border-radius: 8px; text-align: center;">
        <span style="color: var(--text-muted);">Fundo de Emergência: </span>
        <span style="color: var(--accent-cyan); font-weight: 700; font-size: 18px;">${(PATRIMONIO.total / resumo.totalDespesas).toFixed(0)} meses</span>
      </div>
    </div>
  `
}
