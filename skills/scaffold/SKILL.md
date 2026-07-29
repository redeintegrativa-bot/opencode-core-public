---
name: scaffold
description: Gera projetos do zero com estrutura pronta para producao. Suporta multiplos stacks (Next.js, Vite, FastAPI, Express, CLI Python, HTML/CSS).
user-invokable: true
allowed-tools:
  - Read
  - Write
  - Bash
metadata:
  keywords: [scaffold, gerar, projeto, template, boilerplate]
---

# Scaffold

## Description
Gera projetos do zero com estrutura pronta para produção. Suporta múltiplos stacks.

## Activation
Slash command: `/scaffold` ou quando o usuário pedir para criar um projeto novo.

## Parameters
- `type` (obrigatório): Tipo de projeto (`nextjs`, `vite-react`, `fastapi`, `express`, `cli-python`, `html-css`)
- `name` (obrigatório): Nome do projeto
- `dir` (opcional): Diretório de destino (padrão: diretório atual)

## Scaffolds

### Next.js
- App Router + TypeScript
- Tailwind CSS
- ESLint + Prettier
- `.env.example`

### Vite + React
- React + TypeScript
- Vite configurado
- CSS modules ou Tailwind

### FastAPI (Python)
- FastAPI + Uvicorn
- Pydantic models
- SQLAlchemy opcional
- Dockerfile opcional

### Express (Node.js)
- Express + TypeScript
- Routes organizados
- Middleware de erro
- `.env.example`

### CLI Python
- Argument parser (argparse)
- Rich para output colorido
- Logging configurado
- Entry point

### HTML + CSS
- HTML5 semântico
- CSS moderno (flexbox/grid)
- Responsivo
- Meta tags OTIMIZADAS

## Examples

```
User: "Cria um projeto Next.js chamado meu-blog"
Agent: Usa scaffold skill para gerar o projeto completo

User: "Quero uma API FastAPI para gestão de tarefas"
Agent: Gera scaffold FastAPI + SQLAlchemy + Pydantic
```

## Rules
- Pergunte sempre o tipo e nome do projeto
- Crie a estrutura de diretórios completa
- Instale dependências se solicitado
- Deixe `.env.example` sempre
