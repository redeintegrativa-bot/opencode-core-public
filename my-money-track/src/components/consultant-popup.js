import { on } from '../services/event-bus.js'

let insights = []
let isOpen = false

const avatarHTML = `
  <div id="consultant-avatar" style="
    position: fixed; bottom: 140px; right: 24px; width: 56px; height: 56px;
    border-radius: 50%; background: linear-gradient(135deg, var(--accent-purple), var(--accent-cyan));
    display: flex; align-items: center; justify-content: center;
    cursor: pointer; z-index: 900; box-shadow: 0 4px 20px rgba(139,92,246,0.4);
    font-size: 24px; transition: transform 0.3s ease;
    animation: pulse-glow 2s infinite;
  " onclick="document.getElementById('consultant-modal').classList.toggle('open')">
    🧠
  </div>
`

const modalHTML = `
  <div id="consultant-modal" style="
    position: fixed; bottom: 204px; right: 24px; width: 360px; max-height: 480px;
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--radius-xl); z-index: 901;
    display: none; flex-direction: column;
    box-shadow: 0 16px 48px rgba(0,0,0,0.5);
    overflow: hidden;
  ">
    <div style="
      padding: 16px 20px; border-bottom: 1px solid var(--border);
      display: flex; align-items: center; gap: 12px;
      background: linear-gradient(135deg, rgba(139,92,246,0.1), rgba(0,212,255,0.05));
    ">
      <div style="font-size: 24px;">🧠</div>
      <div style="flex:1;">
        <div style="font-weight: 700; font-size: 15px;">Consultor Financeiro</div>
        <div style="font-size: 12px; color: var(--text-muted);">Análises e sugestões</div>
      </div>
      <button onclick="this.closest('#consultant-modal').classList.remove('open')" style="
        background:none; border:none; color:var(--text-muted); cursor:pointer; font-size:20px;
      ">✕</button>
    </div>
    <div id="consultant-body" style="
      flex:1; overflow-y: auto; padding: 16px;
    "></div>
  </div>
`

export function initConsultant() {
  const style = document.createElement('style')
  style.textContent = `
    @keyframes pulse-glow { 0%,100% { box-shadow: 0 4px 20px rgba(139,92,246,0.4); } 50% { box-shadow: 0 4px 30px rgba(139,92,246,0.7); } }
    #consultant-modal.open { display: flex; }
    .consultant-insight { padding: 12px; border-radius: var(--radius-md); margin-bottom: 8px; border: 1px solid var(--border); background: var(--bg-secondary); cursor: pointer; transition: all 0.2s; }
    .consultant-insight:hover { border-color: var(--accent-purple); }
    .consultant-insight-header { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
    .consultant-insight-icon { font-size: 18px; }
    .consultant-insight-title { font-weight: 600; font-size: 13px; }
    .consultant-insight-msg { font-size: 12px; color: var(--text-secondary); line-height: 1.5; }
    .consultant-tag { font-size: 10px; padding: 2px 8px; border-radius: 10px; text-transform: uppercase; font-weight: 600; }
    .tag-positivo { background: rgba(0,212,161,0.15); color: var(--accent-green); }
    .tag-alerta { background: rgba(239,68,68,0.15); color: var(--accent-red); }
    .tag-dica { background: rgba(245,158,11,0.15); color: var(--accent-orange); }
    .tag-info { background: rgba(0,212,255,0.15); color: var(--accent-cyan); }
  `
  document.head.appendChild(style)

  document.body.insertAdjacentHTML('beforeend', avatarHTML + modalHTML)

  on('consultant:insights', (novosInsights) => {
    insights = novosInsights
    render()
  })

  setInterval(() => {
    const el = document.getElementById('consultant-body')
    if (el && isOpen) render()
  }, 30000)
}

export function showInsights(novosInsights) {
  insights = novosInsights
  render()
}

function render() {
  const el = document.getElementById('consultant-body')
  if (!el || !insights.length) return

  el.innerHTML = insights.map(i => `
    <div class="consultant-insight" onclick="navigateTo('consultor')">
      <div class="consultant-insight-header">
        <span class="consultant-insight-icon">${i.icone}</span>
        <span class="consultant-insight-title">${i.titulo}</span>
        <span style="margin-left:auto;"><span class="consultant-tag tag-${i.tipo}">${i.tipo}</span></span>
      </div>
      <div class="consultant-insight-msg">${i.mensagem}</div>
    </div>
  `).join('')
}
