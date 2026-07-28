import { DESPESAS, PATRIMONIO, RECEITAS, getResumoFinanceiro } from '../data.js'

export function renderFinanceiro() {
  const totalDespesas = DESPESAS.reduce((acc, d) => acc + d.valor, 0)
  const resumo = getResumoFinanceiro()

  return `
    <div class="page-header">
      <h1 class="page-title">💰 Financeiro</h1>
      <p class="page-subtitle">Receitas e despesas</p>
    </div>

    <div class="card" style="border-left: 3px solid var(--accent-green); margin-bottom: 16px;">
      <h3 style="margin-bottom: 12px;"><i class="fas fa-arrow-up"></i> Receitas</h3>
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
        ${RECEITAS.filter(r => r.status === 'ativo').map(r => `
          <div style="background: var(--bg-secondary); padding: 12px; border-radius: 8px;">
            <div style="color: var(--text-muted); font-size: 11px;">🎨 ${r.nome}</div>
            <div style="font-weight: 600; color: var(--accent-green);">R$ ${r.valor}</div>
            <div style="font-size: 11px; color: var(--text-muted);">${r.periodicidade}</div>
          </div>
        `).join('')}
      </div>
      <div style="margin-top: 12px; padding: 12px; background: var(--bg-tertiary); border-radius: 8px; text-align: center;">
        <span style="color: var(--text-muted);">Renda mensal (est.): </span>
        <span style="color: var(--accent-green); font-weight: 700; font-size: 18px;">R$ ${resumo.receitaMensal}/mês</span>
      </div>
    </div>

    <div class="card" style="border-left: 3px solid var(--accent-red);">
      <h3 style="margin-bottom: 12px;"><i class="fas fa-receipt"></i> Despesas Mensais</h3>
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
        ${DESPESAS.map(despesa => `
          <div style="background: var(--bg-secondary); padding: 12px; border-radius: 8px;">
            <div style="color: var(--text-muted); font-size: 11px;">${despesa.categoria === 'educacao' ? '📚' : '🏠'} ${despesa.descricao}</div>
            <div style="font-weight: 600;">R$ ${despesa.valor}</div>
            <div style="font-size: 11px; color: var(--text-muted);">${despesa.frequencia}</div>
          </div>
        `).join('')}
      </div>
      <div style="margin-top: 12px; padding: 12px; background: var(--bg-tertiary); border-radius: 8px; text-align: center;">
        <span style="color: var(--text-muted);">Total: </span>
        <span style="color: var(--accent-red); font-weight: 700; font-size: 18px;">R$ ${totalDespesas}/mês</span>
        <span style="color: var(--text-muted);">  |  </span>
        <span style="color: var(--text-muted);">Saldo: </span>
        <span style="color: ${resumo.saldoMensal >= 0 ? 'var(--accent-green)' : 'var(--accent-red)'}; font-weight: 700; font-size: 18px;">R$ ${resumo.saldoMensal}/mês</span>
      </div>
    </div>
  `
}
