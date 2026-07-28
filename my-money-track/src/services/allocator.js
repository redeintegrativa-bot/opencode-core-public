import { INVESTIMENTOS, getResumoFinanceiro } from '../data.js'

export function calcularAlocacaoAtual() {
  const resumo = getResumoFinanceiro()
  const total = resumo.patrimonioTotal
  if (!total) return []

  const classes = {}
  INVESTIMENTOS.forEach(inv => {
    const tipo = inv.tipo === 'acao' ? 'Ações' :
                 inv.tipo === 'fii' ? 'FIIs' :
                 inv.tipo === 'cripto' || inv.tipo === 'stablecoin' ? 'Cripto' :
                 inv.risco === 'baixo' ? 'Renda Fixa' : 'Outros'
    if (!classes[tipo]) classes[tipo] = 0
    classes[tipo] += inv.valor
  })

  return Object.entries(classes).map(([nome, valor]) => ({
    nome,
    valor,
    pct: ((valor / total) * 100).toFixed(1)
  })).sort((a, b) => b.valor - a.valor)
}

export function sugerirRealocacao(alocacaoAtual) {
  const ideal = {
    'Renda Fixa': 70,
    'Ações': 15,
    'FIIs': 5,
    'Cripto': 10
  }

  return Object.entries(ideal).map(([classe, pctIdeal]) => {
    const atual = alocacaoAtual.find(a => a.nome === classe)
    const pctAtual = atual ? parseFloat(atual.pct) : 0
    const diferenca = pctIdeal - pctAtual
    return {
      classe,
      atual: pctAtual,
      ideal: pctIdeal,
      diferenca: diferenca.toFixed(1),
      acao: Math.abs(diferenca) > 5
        ? (diferenca > 0 ? `Aumentar ${diferenca.toFixed(0)}pp` : `Reduzir ${Math.abs(diferenca).toFixed(0)}pp`)
        : 'OK'
    }
  })
}
