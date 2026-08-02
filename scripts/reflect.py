#!/usr/bin/env python3
"""Reflexão automática (mini-Hermes) para o OpenCode.

Varre as sessões salvas do store, detecta padrões recorrentes (temas, tarefas
repetidas, lacunas) e propõe skills/regras em ~/.config/opencode/hermes-staging/.
Nada é instalado automaticamente — tudo passa por revisão humana.

Modos:
  * --scan   (padrão) análise heurística local, sem LLM.
  * --deep   passa extra com `opencode run --format json` para análise semântica.

Uso:
  python3 reflect.py [--root /root] [--scan|--deep] [--list] [--staging DIR]
"""

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "memory"))
from session import SessionStore  # noqa: E402

DEFAULT_STAGING = Path.home() / ".config" / "opencode" / "hermes-staging"

STOPWORDS = {
    "sessão", "sessao", "session", "sessions", "resumo", "corrigido", "corrigida",
    "criada", "criado", "adicionado", "adicionados", "commitado", "commitados",
    "público", "publico", "pessoal", "projeto", "projetos", "projeto.",
    "memória", "memoria", "atualizado", "atualizados", "atualizado,",
    "concluído", "concluido", "github", "repo", "repos", "repositório", "repositorio",
    "via", "agora", "com", "para", "depois", "entre", "sobre", "após", "então",
    "foi", "são", "vai", "feito", "feita", "também", "tambem", "quando", "onde",
    "opencode", "skill", "skills", "registry", "gatilho", "salva", "salvo", "salvando",
    "sessão.", "sessão,",
}
KEYWORD_MIN_LEN = 5
THEME_MIN_COUNT = 3

PROPOSAL_TEMPLATE = """# Proposta: {title}

- **Tipo:** {ptype}
- **Data:** {date}
- **Confiança:** {confidence}
- **Sessões-fonte:** {sessions}
- **Status:** pendente de revisão (em ~/.config/opencode/hermes-staging)

## Por quê

{why}

## Evidências

{examples}

## Rascunho de skill ({slug})

```markdown
---
name: {slug}
description: TODO — {title}
user-invokable: true
---

# {title}

## When to Activate

- {when}

## Core Principle

{principle}

## Fluxo de trabalho

- Passo 1: ...
- Passo 2: ...

## Anti-patterns

- ...
```

---
*Gerado automaticamente por reflect.py — revisar antes de ativar.*
"""

RULE_TEMPLATE = """# Regra proposta: {title}

- **Tipo:** rule
- **Data:** {date}
- **Confiança:** {confidence}
- **Sessões-fonte:** {sessions}
- **Status:** pendente de revisão

## Texto da regra

{rule_text}

## Evidências

{examples}

---
*Gerado automaticamente por reflect.py — revisar antes de ativar.*
"""


def gather_entries(store: SessionStore) -> list:
    entries = []
    for meta in store.sessions_meta():
        f = store.sessions_dir / f"session-{meta['id']}.md"
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        in_log = False
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("**Log:**"):
                in_log = True
                continue
            if line.startswith("**") and in_log:
                in_log = False
            if in_log and line.startswith("- ") and len(line) > 8:
                entries.append({"text": line[2:].strip(), "session": meta["id"], "date": meta["date"]})
    return entries


def tokenize(text: str) -> list:
    return [w.lower() for w in re.findall(r"[A-Za-zÀ-ÿ]{5,}", text)]


def themes_of(entries: list) -> list:
    counts = Counter()
    for e in entries:
        for w in set(tokenize(e["text"])):
            if w not in STOPWORDS and len(w) >= KEYWORD_MIN_LEN:
                counts[w] += 1
    return [w for w, c in counts.most_common() if c >= THEME_MIN_COUNT]


def scan(store: SessionStore) -> list:
    entries = gather_entries(store)
    themes = themes_of(entries)
    proposals = []
    for kw in themes:
        matches = [e for e in entries if kw in tokenize(e["text"])]
        sessions = sorted({m["session"] for m in matches})
        count = len(sessions)
        examples = "\n".join(f"- ({e['date']}) {e['text'][:160]}" for e in matches[:5])
        slug = "auto-" + re.sub(r"[^a-z0-9]+", "-", kw.lower()).strip("-")[:40]
        proposals.append({
            "title": f"Tema recorrente: '{kw}'",
            "ptype": "skill",
            "slug": slug,
            "why": f"O tema '{kw}' apareceu em {count} sessões — indica um fluxo repetido "
                   "que pode virar skill reutilizável.",
            "when": f"Ao trabalhar com {kw}",
            "principle": f"Tratar {kw} de forma consistente entre sessões.",
            "examples": examples,
            "sessions": ", ".join(sessions),
            "count": count,
        })
    return proposals, entries


def deep_analyze(store: SessionStore) -> list:
    entries = gather_entries(store)
    digest = "\n".join(f"- ({e['date']}) {e['text'][:140]}" for e in entries)
    prompt = (
        "Analise o histórico de sessões de um assistente de IA abaixo. Identifique "
        "2-4 padrões reutilizáveis (workflows, regras ou conhecimento de domínio) que "
        "mereceriam virar skills/regras. Para cada um, responda em JSON: "
        '[{"title": "...", "why": "...", "when": "...", "principle": "..."}]. '
        "Histórico:\n" + digest
    )
    try:
        proc = subprocess.run(
            ["opencode", "run", "--pure", "--format", "json", prompt],
            capture_output=True, text=True, timeout=600,
        )
        raw = proc.stdout
        if not raw:
            return []
        data = json.loads(raw)
        text = data.get("result", "") if isinstance(data, dict) else str(data)
        arr = json.loads(text) if isinstance(text, str) and text.strip().startswith("[") else []
        return [
            {"title": it.get("title", "Padrão"), "ptype": "skill",
             "slug": "deep-" + re.sub(r"[^a-z0-9]+", "-", it.get("title", "").lower()).strip("-")[:40],
             "why": it.get("why", ""), "when": it.get("when", ""),
             "principle": it.get("principle", ""), "examples": "Análise semântica (opencode run).",
             "sessions": "—", "count": "?"}
            for it in arr
        ]
    except Exception as e:
        print(f"Deep analysis falhou: {e}", file=sys.stderr)
        return []


def write_proposals(proposals: list, staging: Path):
    stamp = datetime.now().strftime("%Y-%m-%d")
    batch_dir = staging / stamp
    batch_dir.mkdir(parents=True, exist_ok=True)
    index = [f"# Staging {stamp} — {len(proposals)} proposta(s)\n\n"]
    for i, p in enumerate(proposals, 1):
        p = dict(p, date=stamp, confidence=p.get("confidence", f"apareceu em {p.get('count', '?')} sessões"))
        fname = f"proposal-{i:02d}-{p['slug']}.md"
        body = (PROPOSAL_TEMPLATE if p["ptype"] == "skill" else RULE_TEMPLATE).format(**p)
        (batch_dir / fname).write_text(body, encoding="utf-8")
        index.append(f"- [{fname}]({fname}) — {p['title']} ({p['count']} sessões)\n")
    (staging / "README.md").write_text("".join(index), encoding="utf-8")
    return batch_dir


def list_proposals(staging: Path):
    if not staging.exists():
        print("Nenhum staging ainda.")
        return
    for f in sorted(staging.glob("*/*.md")):
        if f.name == "README.md":
            continue
        first = f.read_text(encoding="utf-8").splitlines()[0].replace("# ", "")
        print(f"{f} — {first}")


def main():
    parser = argparse.ArgumentParser(description="Reflexão automática (mini-Hermes)")
    parser.add_argument("--root", default=os.getcwd())
    parser.add_argument("--local", action="store_true")
    parser.add_argument("--staging", default=str(DEFAULT_STAGING))
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--scan", action="store_true", help="Análise heurística (padrão)")
    mode.add_argument("--deep", action="store_true", help="Análise semântica via opencode run")
    parser.add_argument("--list", action="store_true", help="Listar propostas em staging")
    args = parser.parse_args()

    staging = Path(args.staging)
    if args.list:
        list_proposals(staging)
        return 0

    store = SessionStore(args.root, args.local)
    if args.deep:
        proposals = deep_analyze(store)
    else:
        proposals, _ = scan(store)

    if not proposals:
        print("Nenhum padrão recorrente encontrado ainda (mínimo de sessões não atingido).")
        return 0
    batch = write_proposals(proposals, staging)
    print(f"Geradas {len(proposals)} propostas em {batch}", flush=True)
    print("Revisar em ~/.config/opencode/hermes-staging/ antes de ativar qualquer uma.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
