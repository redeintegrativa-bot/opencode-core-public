import { initDB } from './db.js'
import { APP_CONFIG } from './data.js'
import { renderDashboard } from './pages/dashboard.js'
import { renderPlataformas } from './pages/plataformas.js'
import { renderProjecoes } from './pages/projecoes.js'
import { renderAnalise } from './pages/analise.js'
import { renderFinanceiro } from './pages/financeiro.js'
import { renderMovimentos } from './pages/movimentos.js'
import { renderNovidades } from './pages/novidades.js'
import { renderConsultor } from './pages/consultor.js'
import { initConsultant } from './components/consultant-popup.js'
import { gerarInsights } from './services/consultant-engine.js'

let currentPage = 'dashboard'
let privacyMode = false
let charts = {}

const SESSION_KEY = 'myMoney_session'

window.navigateToConsultor = function() { navigateTo('consultor') }

window.handleLogin = function() {
  const password = document.getElementById('password').value
  const appPassword = import.meta.env.VITE_APP_PASSWORD || 'change-me'

  if (password === appPassword || password === '') {
    const session = { loginTime: Date.now(), lastAccess: new Date().toLocaleString('pt-BR') }
    localStorage.setItem(SESSION_KEY, JSON.stringify(session))

    document.getElementById('loginScreen').style.display = 'none'
    document.getElementById('appContainer').style.display = 'block'
    initApp()
  } else {
    document.getElementById('loginError').style.display = 'block'
  }
}

document.getElementById('password').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') window.handleLogin()
})

window.toggleSidebar = function() {
  document.getElementById('sidebar').classList.toggle('open')
  document.getElementById('menuOverlay').classList.toggle('show')
}

window.togglePrivacyMode = function() {
  privacyMode = !privacyMode
  const icon = document.getElementById('privacyIcon')
  icon.className = privacyMode ? 'fas fa-eye-slash' : 'fas fa-eye'

  document.querySelectorAll('.card-value, .platform-detail-value').forEach(el => {
    if (privacyMode) {
      el.dataset.originalValue = el.textContent
      el.textContent = '••••'
    } else if (el.dataset.originalValue) {
      el.textContent = el.dataset.originalValue
    }
  })
}

window.showPageMobile = function(page, btn) {
  document.querySelectorAll('.bottom-nav-item').forEach(item => item.classList.remove('active'))
  btn.classList.add('active')
  navigateTo(page)
}

window.openQuickActions = function() {
  const actions = [
    { icon: 'fa-home', label: 'Resumo', page: 'dashboard' },
    { icon: 'fa-coins', label: 'Carteiras', page: 'plataformas' },
    { icon: 'fa-brain', label: 'Consultor', page: 'consultor' },
    { icon: 'fa-chart-line', label: 'Projeções', page: 'projecoes' },
    { icon: 'fa-wallet', label: 'Financeiro', page: 'financeiro' },
    { icon: 'fa-exchange-alt', label: 'Fluxo', page: 'movimentos' },
    { icon: 'fa-bell', label: 'Novidades', page: 'novidades' }
  ]

  const modal = document.createElement('div')
  modal.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.8);z-index:2000;display:flex;align-items:center;justify-content:center;'
  modal.onclick = (e) => { if (e.target === modal) modal.remove() }

  modal.innerHTML = `
    <div style="background:var(--bg-card);border-radius:20px;padding:24px;width:90%;max-width:320px;border:1px solid var(--border);">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
        <h3 style="font-size:18px;font-weight:600;">Ações Rápidas</h3>
        <button onclick="this.closest('div[style*=fixed]').remove()" style="background:none;border:none;color:var(--text-muted);font-size:20px;cursor:pointer;">✕</button>
      </div>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">
        ${actions.map(a => `
          <button onclick="this.closest('div[style*=fixed]').remove(); setTimeout(() => navigateTo('${a.page}'), 100)" style="background:var(--bg-secondary);border:1px solid var(--border);border-radius:12px;padding:16px 8px;cursor:pointer;transition:all 0.2s;">
            <i class="fas ${a.icon}" style="font-size:20px;margin-bottom:6px;display:block;color:var(--accent-green);"></i>
            <div style="font-size:11px;color:var(--text-secondary);">${a.label}</div>
          </button>
        `).join('')}
      </div>
    </div>
  `
  document.body.appendChild(modal)
}

function navigateTo(page) {
  currentPage = page
  const pagesContainer = document.getElementById('pagesContainer')

  destroyCharts()

  const renderers = {
    dashboard: renderDashboard,
    plataformas: renderPlataformas,
    projecoes: renderProjecoes,
    analise: renderAnalise,
    financeiro: renderFinanceiro,
    movimentos: renderMovimentos,
    novidades: renderNovidades,
    consultor: renderConsultor
  }

  const renderer = renderers[page]
  if (renderer) {
    pagesContainer.innerHTML = '<div class="page-content">' + renderer() + '</div>'
    if (page === 'dashboard' || page === 'analise') {
      setTimeout(() => initCharts(page), 100)
    }
  }

  document.querySelectorAll('.nav-item').forEach(item => {
    item.classList.toggle('active', item.dataset.page === page)
  })

  if (window.innerWidth < 1024) {
    document.getElementById('sidebar').classList.remove('open')
    document.getElementById('menuOverlay').classList.remove('show')
  }

  window.scrollTo({ top: 0, behavior: 'smooth' })
}
window.navigateTo = navigateTo

function destroyCharts() {
  Object.values(charts).forEach(chart => {
    if (chart && typeof chart.destroy === 'function') {
      chart.destroy()
    }
  })
  charts = {}
}

function initCharts(page) {
  if (page === 'dashboard') {
    return
  }

  if (page === 'analise') {
    const ctx2 = document.getElementById('patrimonioChart')
    if (ctx2) {
      charts.patrimonio = new Chart(ctx2, {
        type: 'doughnut',
        data: {
          labels: ['Baixo Risco', 'Alto Risco'],
          datasets: [{
            data: [10590, 2835],
            backgroundColor: ['#00d4ff', '#8b5cf6'],
            borderWidth: 0
          }]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
      })
    }

    const ctx3 = document.getElementById('despesasChart')
    if (ctx3) {
      charts.despesas = new Chart(ctx3, {
        type: 'bar',
        data: {
          labels: ['Patrimônio', 'Despesas (x12)'],
          datasets: [{
            data: [13425, 4800],
            backgroundColor: ['#00d4a1', '#ef4444'],
            borderRadius: 8
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { grid: { display: false }, ticks: { color: '#71717a' } },
            y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#71717a', callback: v => 'R$ ' + v } }
          }
        }
      })
    }
  }
}

function updateDateTime() {
  const now = new Date()
  const DIAS = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']
  const MESES = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
  const dataStr = `${DIAS[now.getDay()]}, ${now.getDate()} de ${MESES[now.getMonth()]} de ${now.getFullYear()}`
  const horaStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
  const el = document.getElementById('currentDateTime')
  if (el) el.textContent = `${dataStr} • ${horaStr}`
}

function initMenu() {
  const menuItems = [
    { id: 'dashboard', icon: 'fa-home', label: 'Resumo' },
    { id: 'plataformas', icon: 'fa-coins', label: 'Carteiras' },
    { id: 'consultor', icon: 'fa-brain', label: 'Consultor', badge: 'NOVO' },
    { id: 'projecoes', icon: 'fa-chart-line', label: 'Projeções' },
    { id: 'analise', icon: 'fa-chart-pie', label: 'Análise' },
    { id: 'financeiro', icon: 'fa-wallet', label: 'Financeiro' },
    { id: 'movimentos', icon: 'fa-exchange-alt', label: 'Fluxo' },
    { id: 'novidades', icon: 'fa-bell', label: 'Novidades' }
  ]

  const navMenu = document.getElementById('navMenu')
  navMenu.innerHTML = menuItems.map(item => `
    <a class="nav-item ${item.id === 'dashboard' ? 'active' : ''}" data-page="${item.id}" onclick="navigateTo('${item.id}')">
      <i class="fas ${item.icon}"></i>
      <span>${item.label}</span>
      ${item.badge ? `<span class="badge green" style="margin-left: auto;">${item.badge}</span>` : ''}
    </a>
  `).join('')
}

async function initApp() {
  try {
    await initDB()
  } catch (e) {
    console.warn('IndexedDB not available, using memory only')
  }

  initMenu()
  updateDateTime()
  setInterval(updateDateTime, 60000)
  initConsultant()
  gerarInsights()
  navigateTo('dashboard')
}

window.addEventListener('load', () => {
  const session = JSON.parse(localStorage.getItem(SESSION_KEY) || '{}')
  if (session.loginTime) {
    const hoursSinceLogin = (Date.now() - session.loginTime) / (1000 * 60 * 60)
    if (hoursSinceLogin < 24) {
      document.getElementById('loginScreen').style.display = 'none'
      document.getElementById('appContainer').style.display = 'block'
      initApp()
    }
  }
})
