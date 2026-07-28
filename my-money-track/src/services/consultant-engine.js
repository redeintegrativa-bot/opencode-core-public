import { getResumoFinanceiro, INVESTIMENTOS, DESPESAS, RECEITAS } from '../data.js'
import { emit } from './event-bus.js'

export function gerarInsights() {
  const resumo = getResumoFinanceiro()
  const insights = []

  const rendaFixa = INVESTIMENTOS.filter(i => i.risco === 'baixo').reduce((a, i) => a + i.valor, 0)
  const rendaVariavel = INVESTIMENTOS.filter(i => i.risco === 'medio' || i.risco === 'alto').reduce((a, i) => a + i.valor, 0)
  const pctFixa = (rendaFixa / resumo.patrimonioTotal) * 100
  const pctVariavel = (rendaVariavel / resumo.patrimonioTotal) * 100

  if (resumo.receitaSemanal > 0) {
    insights.push({
      tipo: 'positivo',
      icone: '💰',
      titulo: 'Nova renda semanal',
      mensagem: `Receita de R$ ${resumo.receitaSemanal}/semana entrando na conta. ${resumo.saldoMensal >= 0 ? 'Saldo positivo de R$ ' + resumo.saldoMensal + '/mês!' : 'Ainda faltam R$ ' + Math.abs(resumo.saldoMensal) + '/mês para equilibrar as contas.'}`
    })
  }

  const granaParada = INVESTIMENTOS.filter(i => i.retorno === 0 && i.risco === 'baixo').reduce((a, i) => a + i.valor, 0)
  if (granaParada > 1000) {
    insights.push({
      tipo: 'alerta',
      icone: '⚠️',
      titulo: 'Dinheiro parado',
      mensagem: `R$ ${granaParada.toFixed(0)} em contas sem rendimento (99 Pay, Nubank Conta, Mercado Pago). Considere mover para a Caixinha Nubank (11,5% a.a.).`
    })
  }

  if (pctVariavel > 40) {
    insights.push({
      tipo: 'alerta',
      icone: '📈',
      titulo: 'Exposição a risco',
      mensagem: `${pctVariavel.toFixed(0)}% em renda variável. Considere reduzir para no máximo 30% do patrimônio.`
    })
  }

  const mesesCobertura = resumo.patrimonioTotal / resumo.totalDespesas
  if (mesesCobertura < 6) {
    insights.push({
      tipo: 'alerta',
      icone: '🛡️',
      titulo: 'Fundo de emergência',
      mensagem: `Apenas ${mesesCobertura.toFixed(0)} meses de despesas cobertos. Ideal: 6 a 12 meses.`
    })
  } else if (mesesCobertura >= 6) {
    insights.push({
      tipo: 'positivo',
      icone: '✅',
      titulo: 'Fundo de emergência OK',
      mensagem: `${mesesCobertura.toFixed(0)} meses de cobertura. Dentro do recomendado!`
    })
  }

  if (pctFixa > 80) {
    insights.push({
      tipo: 'dica',
      icone: '💡',
      titulo: 'Muito conservador',
      mensagem: `${pctFixa.toFixed(0)}% em renda fixa. Com 20-30 anos de horizonte, pode aumentar exposição a variável.`
    })
  }

  RECEITAS.filter(r => r.status === 'ativo').forEach(r => {
    insights.push({
      tipo: 'info',
      icone: '📋',
      titulo: r.nome,
      mensagem: `R$ ${r.valor}/${r.periodicidade} — ${r.descricao}`
    })
  })

  emit('consultant:insights', insights)
  return insights
}

export function getSugestoesAlocacao() {
  const resumo = getResumoFinanceiro()
  const patrimonio = resumo.patrimonioTotal

  return {
    reservaEmergencia: {
      pct: 30,
      valor: patrimonio * 0.3,
      destino: 'Nubank Caixinha (11,5% a.a.)'
    },
    rendaFixa: {
      pct: 40,
      valor: patrimonio * 0.4,
      destino: 'Ripio WBRL (15% a.a.) + Caixinha'
    },
    acoes: {
      pct: 20,
      valor: patrimonio * 0.2,
      destino: 'ITSA4, TOTS3, ETF BOVA11'
    },
    cripto: {
      pct: 10,
      valor: patrimonio * 0.1,
      destino: 'Bitcoin + USDT (Ripio)'
    }
  }
}
