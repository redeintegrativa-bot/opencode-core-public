const DICAS = [
  {
    icone: '🎯',
    titulo: 'Diversificação',
    mensagem: 'Nunca dependa de uma única fonte de renda. Busque múltiplos fluxos de receita!'
  },
  {
    icone: '💰',
    titulo: 'Juros Compostos',
    mensagem: 'Invista regularmente e deixe os juros compostos trabalharem a seu favor.'
  },
  {
    icone: '🛡️',
    titulo: 'Fundo de Emergência',
    mensagem: 'Ideal: 6 a 12 meses de despesas parados em renda fixa com liquidez diária.'
  },
  {
    icone: '📊',
    titulo: 'Acompanhamento',
    mensagem: 'Revise sua carteira a cada 3 meses. Rebalanceie se necessário.'
  },
  {
    icone: '💳',
    titulo: 'Carteiras Digitais',
    mensagem: 'Saldo parado não rende. Transfira para investimentos com liquidez.'
  },
  {
    icone: '₿',
    titulo: 'Criptomoedas',
    mensagem: 'Máximo 10-15% do patrimônio em cripto. Alta volatilidade.'
  },
  {
    icone: '📈',
    titulo: 'Ações',
    mensagem: 'Invista com horizonte de longo prazo. Evite day trade.'
  },
  {
    icone: '🎓',
    titulo: 'Educação',
    mensagem: 'Invista em conhecimento. É o ativo com maior retorno possível.'
  }
]

export function getDicaDoDia() {
  const hoje = new Date().getDate()
  return DICAS[hoje % DICAS.length]
}

export function getTodasDicas() {
  return DICAS
}
