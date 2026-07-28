import { NUBANK, PAY99, MERCADO_PAGO, RIPIO, RECEITAS } from '../data.js'

export function renderPlataformas() {
  return `
    <div class="page-header">
      <h1 class="page-title">Carteiras e Rendas</h1>
      <p class="page-subtitle">Contas, ativos e fontes de renda</p>
    </div>

    <div class="platform-card" style="border-left: 3px solid var(--accent-green);">
      <div class="platform-header">
        <div>
          <div class="platform-name">🎨 Renda Principal</div>
          <div class="card-sublabel">${RECEITAS[0].descricao}</div>
        </div>
        <span class="platform-status ativo">ATIVO</span>
      </div>
      <div class="platform-details">
        <div class="platform-detail"><div class="platform-detail-label">Valor</div><div class="platform-detail-value" style="color: var(--accent-green);">R$ ${RECEITAS[0].valor}</div></div>
        <div class="platform-detail"><div class="platform-detail-label">Periodicidade</div><div class="platform-detail-value">${RECEITAS[0].periodicidade}</div></div>
        <div class="platform-detail"><div class="platform-detail-label">Mensal (est.)</div><div class="platform-detail-value" style="color: var(--accent-green);">R$ ${RECEITAS[0].valor * 4}</div></div>
        <div class="platform-detail"><div class="platform-detail-label">Anual (est.)</div><div class="platform-detail-value" style="color: var(--accent-green);">R$ ${RECEITAS[0].valor * 52}</div></div>
      </div>
    </div>

    <div class="platform-card">
      <div class="platform-header">
        <div>
          <div class="platform-name">💳 99 Pay</div>
          <div class="card-sublabel">Carteira Digital</div>
        </div>
        <span class="platform-status ativo">ATIVO</span>
      </div>
      <div class="platform-details">
        <div class="platform-detail"><div class="platform-detail-label">Saldo</div><div class="platform-detail-value">R$ ${PAY99.valor.toFixed(2)}</div></div>
      </div>
    </div>

    <div class="platform-card">
      <div class="platform-header">
        <div>
          <div class="platform-name">🏦 Nubank</div>
          <div class="card-sublabel">Caixinha + Conta + Bitcoin</div>
        </div>
        <span class="platform-status ativo">ATIVO</span>
      </div>
      <div class="platform-details">
        <div class="platform-detail"><div class="platform-detail-label">Caixinha</div><div class="platform-detail-value">R$ ${NUBANK.caixinha.toFixed(2)}</div></div>
        <div class="platform-detail"><div class="platform-detail-label">Conta Corrente</div><div class="platform-detail-value">R$ ${NUBANK.conta.toFixed(2)}</div></div>
        <div class="platform-detail"><div class="platform-detail-label">Bitcoin</div><div class="platform-detail-value">R$ ${NUBANK.bitcoin.toFixed(0)}</div></div>
        <div class="platform-detail"><div class="platform-detail-label">Total</div><div class="platform-detail-value" style="color: var(--accent-cyan);">R$ ${NUBANK.total.toFixed(2)}</div></div>
      </div>
    </div>

    <div class="platform-card">
      <div class="platform-header">
        <div>
          <div class="platform-name">💚 Mercado Pago</div>
          <div class="card-sublabel">Carteira Digital</div>
        </div>
        <span class="platform-status ativo">ATIVO</span>
      </div>
      <div class="platform-details">
        <div class="platform-detail"><div class="platform-detail-label">Saldo</div><div class="platform-detail-value">R$ ${MERCADO_PAGO.valor.toFixed(2)}</div></div>
      </div>
    </div>

    <div class="platform-card">
      <div class="platform-header">
        <div>
          <div class="platform-name">₿ Ripio</div>
          <div class="card-sublabel">WBRL + USDT</div>
        </div>
        <span class="platform-status ativo">INVESTIMENTO</span>
      </div>
      <div class="platform-details">
        <div class="platform-detail"><div class="platform-detail-label">WBRL</div><div class="platform-detail-value">R$ ${RIPIO.wbrl.toFixed(2)}</div></div>
        <div class="platform-detail"><div class="platform-detail-label">USDT</div><div class="platform-detail-value">R$ ${RIPIO.usdt.toFixed(2)}</div></div>
        <div class="platform-detail"><div class="platform-detail-label">Total</div><div class="platform-detail-value" style="color: var(--accent-green);">R$ ${RIPIO.total.toFixed(2)}</div></div>
      </div>
    </div>
  `
}
