---
name: mcp-discovery
description: Descobrir e adicionar servidores MCP sob demanda consultando o diretório mcpservers.org. Use quando o usuário pedir para integrar uma ferramenta/serviço via MCP, quando precisar de um servidor MCP novo (banco, busca, scraping, nuvem, etc.), ou quando mencionar "mcpservers.org", "catálogo de MCP", "add MCP" ou "adicionar servidor MCP".
user-invokable: true
allowed-tools: Read, Write, Grep, Glob, Bash
metadata:
  keywords: [mcp, mcpservers, discover, servidor, server, integração, add-mcp, catálogo, on-demand]
---

# MCP Discovery (on demand)

Descobre servidores MCP no diretório [mcpservers.org](https://mcpservers.org) e os adiciona
à configuração do opencode (`~/.config/opencode/opencode.jsonc`). A skill é acionada **sob demanda**:
não registra nenhum servidor permanentemente — cada servidor é ativado por escolha explícita do usuário.

## Core Principle

O catálogo é a fonte: antes de escrever um servidor MCP do zero (ver skill `mcp-builder`), procure
no mcpservers.org se já existe um mantido pela comunidade ou oficial. Se existir, basta configurá-lo
no opencode com `type: local` (npx/uvx) ou `type: remote` (URL). Só partir para o `mcp-builder` quando
não houver alternativa pronta.

## When to Activate

- Usuário pede para integrar um serviço via MCP (ex.: "quero MCP do Notion", "add MCP de busca", "conecta meu banco").
- Usuário menciona `mcpservers.org`, "catálogo de MCP", "adicionar servidor MCP", "instalar MCP".
- Uma skill/task precisa de uma ferramenta externa que ainda não está configurada no opencode.

## Fluxo de trabalho

### 1. Descobrir o servidor

Consulte o catálogo (preferência por `webfetch`; fallback `curl`):

- Categorias: `https://mcpservers.org/category/<nome>` (development, productivity, database, search, web-scraping, file-system, version-control, communication, cloud-service, cloud-storage, marketing, finance, design, memory, other)
- Todos: `https://mcpservers.org/all`
- Oficiais: `https://mcpservers.org/official`
- Remotos (URL, sem instalação): `https://mcpservers.org/remote-mcp-servers`
- Busca: use o buscador web com `site:mcpservers.org <ferramenta>` quando o catálogo não tiver busca própria.

Cada card do catálogo leva a uma página `/servers/<org>/<nome>` com: descrição, repositório,
comando de instalação (`npx`, `uvx`, `pip`, `git clone`) ou URL remota, e credenciais/headers necessários.

### 2. Extrair o comando de instalação

Da página do servidor, capture:

- **Local (stdio)**: comando e argumentos. Ex.: `npx -y mcp-remote https://mcp.sleekplan.com/mcp` → `command: ["npx", "-y", "mcp-remote", "https://mcp.sleekplan.com/mcp"]`.
- **Remoto (URL)**: endpoint HTTP/SSE e headers exigidos (ex.: `Authorization: Bearer <token>`).
- **Variáveis de ambiente**: chaves de API e onde obtê-las (nunca invente valores).

### 3. Configurar no opencode

Edite `~/.config/opencode/opencode.jsonc`, bloco `"mcp"`:

```jsonc
{
  "mcp": {
    "meu-servidor": {
      "type": "local",
      "command": ["npx", "-y", "nome-do-pacote"],
      "enabled": true,
      "environment": { "API_KEY": "${API_KEY}" }
    },
    "servidor-remoto": {
      "type": "remote",
      "url": "https://exemplo.com/mcp",
      "headers": { "Authorization": "Bearer ${TOKEN}" }
    }
  }
}
```

- `type` é obrigatório (`local` ou `remote`).
- `command` é sempre um **array** de strings, nunca uma string única.
- Use `${VAR}` para segredos — nunca grave tokens/chaves no arquivo.

### 4. Verificar e comunicar

- Valide o JSON depois de editar (o opencode rejeita config inválida e não inicia).
- Avise o usuário que **a config só carrega ao reiniciar o opencode**.
- Confirme se o servidor exige credencial que o usuário precisa obter/prover.

## Anti-patterns

- ❌ Adicionar servidores MCP que o usuário não pediu (a skill é sob demanda).
- ❌ Criar um servidor do zero (`mcp-builder`) sem antes checar o catálogo.
- ❌ Hardcodar tokens/API keys no `opencode.jsonc`.
- ❌ Usar `command` como string única ou omitir `type`.
- ❌ Copiar URL de instalação sem confirmar que é do mantenedor oficial.
