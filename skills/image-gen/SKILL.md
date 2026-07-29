---
name: image-gen
description: Geração de imagens via API (Replicate, FAL, Stability AI). Use /image para criar imagens programaticamente.
user-invokable: true
allowed-tools: Read, Write, Bash, Task
metadata:
  keywords: [image, generate, ai, stable-diffusion, flux, replicate, fal, imagem, gerar]
---

# Image Generation Skill

## Purpose

Gerar imagens via API a partir de descrições textuais. Suporta Replicate (FLUX, SD), FAL (FLUX Schnell), e Stability AI (SD3.5).

## Trigger

- `/image <prompt>` — gera imagem com configurações padrão
- `/image <prompt> --model flux-schnell --size 1024x1024` — gera com opções

## Providers Disponíveis

| Provider | Modelos | Preço/Imagem | Free Tier | Chave via env var |
|----------|---------|-------------|-----------|------------------|
| Replicate | FLUX.1 Schnell, FLUX.1 Pro, SDXL | $0.003-$0.035 | Playground limitado | `REPLICATE_API_KEY` |
| FAL | FLUX.1 Schnell, FLUX.1 Pro | $0.003-$0.025 | — | `FAL_KEY` |
| Stability AI | SD3.5 Large, Medium, Flash | $0.01-$0.08 | 25 credits | `STABILITY_API_KEY` |

### Recomendação

- **Mais barato**: FLUX Schnell via FAL ($0.003/imagem) — melhor qualidade-preço
- **Qualidade máxima**: FLUX Pro via Replicate ($0.035/imagem)
- **Teste grátis**: Stability AI (25 credits, ~8-10 imagens SD3.5 Flash)

## Algoritmo

### 1. Escolher Provider

- Se `FAL_KEY` existe → usar FAL (mais barato)
- Se não, `REPLICATE_API_KEY` → usar Replicate
- Se nenhuma chave → avisar "Configure REPLICATE_API_KEY ou FAL_KEY no .env"

### 2. Executar API

Usar Bash + curl no provider escolhido:

```bash
# FAL - FLUX Schnell
curl -s -X POST "https://fal.run/fal-ai/flux-schnell" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "<prompt>", "image_size": "1024x1024"}'

# Replicate - FLUX Schnell
curl -s -X POST "https://api.replicate.com/v1/models/black-forest-labs/flux-schnell/predictions" \
  -H "Authorization: Token $REPLICATE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": {"prompt": "<prompt>", "num_outputs": 1, "aspect_ratio": "1:1"}}'

# Stability AI - SD3.5
curl -s -X POST "https://api.stability.ai/v2beta/stable-image/generate/sd3" \
  -H "authorization: $STABILITY_API_KEY" \
  -H "accept: application/json" \
  -F "prompt=<prompt>" \
  -F "model=sd3.5-medium" \
  -F "output_format=jpeg"
```

### 3. Salvar

- Salva imagem em `./assets/` com nome `{slug-do-prompt}-{timestamp}.{ext}`
- Registra custo em `~/.config/opencode/knowledge/image-gen-costs.jsonl`

### 4. Retornar

- Exibe preview inline (se terminal suporta) ou caminho do arquivo
- Mostra custo da operação: "+$0.003 (FLUX Schnell via FAL)"

## Prompt Engineering para Imagens

| Técnica | Exemplo |
|---------|---------|
| Adjetivos visuais | "cinematic lighting, 8k, photorealistic" |
| Estilo | "oil painting by Monet, vector art, pixel art" |
| Sujeito claro | "a golden retriever wearing a top hat" |
| Negativo | `--negative "blurry, distorted, extra fingers"` |
| Aspect Ratio | "16:9", "9:16", "1:1", "4:3" |

## Custo Tracking

- Salva cada chamada em `knowledge/image-gen-costs.jsonl`
  ```json
  {"timestamp": "2026-07-28T23:45:00", "prompt": "gato astronauta", "model": "flux-schnell", "cost": 0.003, "provider": "fal"}
  ```
- `/image-cost` — mostra total gasto no mês

## Edge Cases

- Se FAL falhar (rate limit), fallback automático para Replicate
- Se todas as APIs falharem, avisar e sugerir Stability AI free tier
- Prompts > 1000 chars: truncar com aviso
- Sem chave configurada: mostrar tutorial de 1 linha pra criar conta
