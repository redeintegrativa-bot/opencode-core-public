/*
 * My Money Track - Template de Controle Financeiro
 * ================================================
 * 
 * 💡 SUGESTÃO REDE INTEGRATIVA:
 *    Este é um app pré-pronto para você adaptar ao seu controle financeiro!
 *    Basta substituir os dados abaixo pelos seus e customizar as categorias.
 *    
 *    Precisa de ajuda? Peça ao assistente OpenCode:
 *      "Me ajuda a configurar o My Money Track com minhas finanças"
 *    
 *    Quer um sistema mais avançado? Fale com a Rede Integrativa:
 *      → https://github.com/redeintegrativa-bot
 * 
 * ================================================
 * DADOS DE EXEMPLO - Substitua pelos seus!
 * ================================================
 */

export const APP_CONFIG = {
  nome: 'My Money Track',
  versao: '2.0.0',
  moeda: 'BRL',
  formatoData: 'dd/MM/yyyy',
  timezone: 'America/Sao_Paulo'
}

export const DESPESAS = [
  { descricao: 'Aluguel', valor: 1500, categoria: 'moradia', frequencia: 'mensal' },
  { descricao: 'Supermercado', valor: 600, categoria: 'alimentacao', frequencia: 'mensal' },
  { descricao: 'Internet', valor: 120, categoria: 'moradia', frequencia: 'mensal' },
  { descricao: 'Transporte', valor: 250, categoria: 'transporte', frequencia: 'mensal' },
  { descricao: 'Streaming', valor: 50, categoria: 'lazer', frequencia: 'mensal' }
]

export const NUBANK = {
  nome: 'Nubank',
  caixinha: 5000.00,
  conta: 2500.00,
  bitcoin: 1000,
  total: 8500.00,
  retorno: 0.5,
  status: 'passivo'
}

export const PAY99 = {
  nome: '99 Pay',
  tipo: 'carteira',
  valor: 1000.00,
  retorno: 0,
  status: 'ativo'
}

export const MERCADO_PAGO = {
  nome: 'Mercado Pago',
  tipo: 'carteira',
  valor: 500.00,
  retorno: 0,
  status: 'ativo'
}

export const RIPIO = {
  nome: 'Ripio',
  tipo: 'cripto',
  wbrl: 500.00,
  usdt: 200.00,
  total: 700.00,
  retorno: 10,
  status: 'investimento'
}

export const INVESTIMENTOS = [
  { nome: '99 Pay', tipo: 'carteira', valor: 1000.00, retorno: 0, risco: 'baixo' },
  { nome: 'Nubank Caixinha', tipo: 'renda_fixa', valor: 5000.00, retorno: 11.5, risco: 'baixo' },
  { nome: 'Nubank Conta', tipo: 'conta_corrente', valor: 2500.00, retorno: 0, risco: 'baixo' },
  { nome: 'Mercado Pago', tipo: 'carteira', valor: 500.00, retorno: 0, risco: 'baixo' },
  { nome: 'Bitcoin Nubank', tipo: 'cripto', valor: 1000, retorno: 0, risco: 'alto' },
  { nome: 'Ripio WBRL', tipo: 'renda_fixa', valor: 500, retorno: 15, risco: 'baixo' },
  { nome: 'Ripio USDT', tipo: 'stablecoin', valor: 200, retorno: 0, risco: 'baixo' }
]

export const PATRIMONIO = {
  total: 10700,
  nubankCaixinha: 5000,
  nubankConta: 2500,
  nubankBitcoin: 1000,
  pay99: 1000,
  mercadoPago: 500,
  ripio: 700
}

export const DIAS = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']
export const MESES = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

export const RECEITAS = [
  {
    id: 'principal',
    nome: 'Salário',
    descricao: 'Renda mensal principal',
    valor: 3500,
    periodicidade: 'mensal',
    status: 'ativo'
  }
]

export function getResumoFinanceiro() {
  const totalDespesas = DESPESAS.reduce((acc, d) => acc + d.valor, 0)
  const receitaSemanal = RECEITAS.filter(r => r.status === 'ativo').reduce((acc, r) => {
    if (r.periodicidade === 'semanal') return acc + r.valor
    if (r.periodicidade === 'mensal') return acc + r.valor / 4
    if (r.periodicidade === 'anual') return acc + r.valor / 52
    return acc
  }, 0)
  const receitaMensal = receitaSemanal * 4
  const saldoMensal = receitaMensal - totalDespesas

  return {
    comissaoDiaria: receitaSemanal / 7,
    receitaMensal,
    receitaSemanal,
    receitaAnual: receitaSemanal * 52,
    totalDespesas,
    saldoMensal,
    patrimonioTotal: PATRIMONIO.total
  }
}
