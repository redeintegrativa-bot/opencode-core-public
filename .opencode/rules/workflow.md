# Regras de Workflow para OpenCode

## Fluxo padrão
1. Entenda o que o usuário quer
2. Consulte skills/registry.json para rotear
3. Use skills relevantes
4. Valide com hooks/validate_security.py
5. Apresente resultado claro

## Termux / Android
- Sem browser (lynx/curl para web)
- Sem Docker
- Python3 + Node.js disponíveis
- Armazenamento local

## Windows (PowerShell)
- Use `python` ao invés de `python3`
- Paths com `\`
- Scripts .ps1 para automação

## Linux
- `python3` disponível
- Paths POSIX
- Scripts .sh para automação
