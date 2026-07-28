# Security by Design Middleware

> **Middleware persistente e inegociável** no Core do Orquestrador.
> Nada futuro escapa dessas regras.

## Fluxo de Vida Seguro

```
CRIAÇÃO/ALTERAÇÃO
       │
       ▼
┌─────────────────┐
│  1. GATEKEEPER   │ ← Validação automática de compliance
│  (pré-gravação)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  2. ZERO-TRUST   │ ← Bloqueio de credenciais + sanitização
│  (em tempo real) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  3. TEMPLATE     │ ← Qualidade automática + logs estruturados
│  (padrão Core)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  4. VALIDAÇÃO    │ ← Pre-commit hook obrigatório
│  (pré-commit)    │
└────────┬────────┘
         │
         ▼
    COMMIT SEGURO ✓
```

## Regras Implementadas

### Regra 101: Gatekeeper de Segurança
- Toda criação passa por validação automática ANTES de gravar
- Script: `hooks/security-gatekeeper.sh`

### Regra 102: Zero-Trust Permanente
- Bloqueio automático de: API keys, tokens, senhas, credenciais
- Sanitização de dados sensíveis em output
- Detecção de padrões: `sk-*`, `ghp_*`, `AKIA*`, `password=`, `secret=`

### Regra 103: Template de Qualidade
- Todo código nasce com: try/catch, logging estruturado, tratamento de erros
- Self-healing: logs formatados para auto-correção

### Regra 104: Validação de Versionamento
- Pre-commit hook obrigatório
- Bloqueia commits com: secrets, .env, padrões perigosos
- Script: `hooks/pre-commit-security.sh`

## Uso

### Scan manual de um diretório
```bash
./hooks/security-gatekeeper.sh /path/to/project
```

### Instalar pre-commit hook
```bash
cp hooks/pre-commit-security.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### Scan antes de commit
```bash
./hooks/pre-commit-security.sh
```

## Padrões Detectados

| Tipo | Padrões |
|------|---------|
| API Keys | `sk-*`, `ghp_*`, `AKIA*`, `api_key=`, `apikey:` |
| Tokens | `token=`, `bearer `, `authorization:` |
| Senhas | `password=`, `passwd=`, `secret=` |
| Configs | Hardcoded credentials em JSON/YAML/TOML |
| Perigosos | `eval()`, `exec()`, `os.system()`, `shell=True` |
| Logs | Dados sensíveis em print/log/console.log |

## Integração com Orquestrador

O Orquestrador V12.5.2+ executa este middleware em:
- **STEP 4** (Decompose): Validação de segurança na criação de tasks
- **STEP 6** (Execute): Gatekeeper antes de cada alteração de código
- **STEP 8** (Verify): Verificação de segurança no review
- **STEP 11** (Cleanup): Sanitização de dados sensíveis em logs
