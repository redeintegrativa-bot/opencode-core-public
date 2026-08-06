# OpenCode Core (pessoal) — Comandos
# Repo personalizado: check-update compara com o publico

.PHONY: help check-update update diff

help:  ## Mostra esta ajuda
	@python -c "
import re
with open('Makefile') as f:
    for line in f:
        m = re.match(r'^([a-zA-Z_-]+):.*## (.+)', line)
        if m:
            print(f'  {m.group(1):15s} {m.group(2)}')
" 2>/dev/null || echo "make: check-update, update, diff"

check-update:  ## Verifica novidades no repositorio publico
	python scripts/check-update.py 2>/dev/null || python3 scripts/check-update.py

update:  ## Copia arquivos novos do publico (revisar alterados manualmente)
	python scripts/update.py 2>/dev/null || python3 scripts/update.py

diff:  ## Mostra o diff publico x local sem copiar
	python scripts/update.py --check 2>/dev/null || python3 scripts/update.py --check
