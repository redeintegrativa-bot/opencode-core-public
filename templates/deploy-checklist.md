# Checklist de Publicacao Segura

## Antes do deploy
- [ ] Repositorio e branch confirmados.
- [ ] Alteracoes revisadas com `git diff --check`.
- [ ] Testes e build aplicaveis executados.
- [ ] Variaveis de ambiente e segredos conferidos sem exibi-los no terminal.
- [ ] Caminho/base de deploy confirmado.

## Preview
- [ ] Preview criado sem substituir a producao.
- [ ] Rota raiz validada.
- [ ] Rotas criticas validadas.
- [ ] Conteudo e responsividade revisados.

## Producao
- [ ] Aprovacao explicita recebida.
- [ ] Preview promovido ou deploy produtivo executado.
- [ ] URL final e rotas criticas retornam sucesso.
- [ ] Commit e referencia do deploy registrados.
