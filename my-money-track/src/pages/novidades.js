import { INVESTIMENTOS, PATRIMONIO, getResumoFinanceiro } from '../data.js'
import { getTodasDicas, getDicaDoDia } from '../services/news-engine.js'

export function renderNovidades() {
  const now = new Date()
  const resumo = getResumoFinanceiro()
  const todasDicas = getTodasDicas()
  const dicaDoDia = getDicaDoDia()

  return `
    <div class="page-header">
      <h1 class="page-title">🔔 Novidades</h1>
      <p class="page-subtitle">Feed + Insights</p>
    </div>

    <div class="card" style="cursor: pointer;">
      <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
        <div style="width: 40px; height: 40px; border-radius: 10px; background: var(--bg-secondary); display: flex; align-items: center; justify-content: center; font-size: 18px;">📊</div>
        <div>
          <div style="font-weight: 600; font-size: 15px;">Resumo da Carteira</div>
          <div style="font-size: 11px; color: var(--text-muted);">${now.toLocaleDateString('pt-BR', { weekday: 'long', day: 'numeric', month: 'long' })}</div>
        </div>
      </div>
      <div style="display: flex; justify-content: space-between; padding: 8px 0;">
        <span>💰 Patrimônio Total</span>
        <span style="color: var(--accent-green); font-weight: 600;">R$ ${PATRIMONIO.total.toLocaleString('pt-BR')}</span>
      </div>
      <div style="display: flex; justify-content: space-between; padding: 8px 0; border-top: 1px solid var(--border);">
        <span>💰 Renda Semanal</span>
        <span style="color: var(--accent-green); font-weight: 600;">R$ ${resumo.receitaSemanal}</span>
      </div>
      <div style="display: flex; justify-content: space-between; padding: 8px 0; border-top: 1px solid var(--border);">
        <span>📦 Ativos na Carteira</span>
        <span style="color: var(--accent-cyan); font-weight: 600;">${INVESTIMENTOS.length}</span>
      </div>
    </div>

    <div class="card" style="cursor: pointer; margin-top: 16px;">
      <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
        <div style="width: 40px; height: 40px; border-radius: 10px; background: var(--bg-secondary); display: flex; align-items: center; justify-content: center; font-size: 18px;">💡</div>
        <div>
          <div style="font-weight: 600; font-size: 15px;">Dica do Dia</div>
          <div style="font-size: 11px; color: var(--text-muted);">${dicaDoDia.titulo}</div>
        </div>
      </div>
      <div style="padding: 12px; background: rgba(0,212,161,0.1); border-radius: 8px; border-left: 3px solid var(--accent-green);">
        ${dicaDoDia.icone} ${dicaDoDia.mensagem}
      </div>
    </div>

    <div class="card" style="margin-top: 16px;">
      <h3 style="margin-bottom: 12px;"><i class="fas fa-book"></i> Biblioteca de Dicas</h3>
      <div style="font-size: 13px; color: var(--text-secondary); line-height: 1.6;">
        ${todasDicas.map(d => `
          <p style="margin-top: 8px;"><strong>${d.icone} ${d.titulo}:</strong> ${d.mensagem}</p>
        `).join('')}
      </div>
    </div>
  `
}
