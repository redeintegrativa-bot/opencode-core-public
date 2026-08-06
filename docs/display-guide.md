# Guia — Fonte pequena no opencode (Windows Terminal)

O opencode roda dentro do terminal e **não controla o tamanho da fonte**.
Quem desenha o texto é o emulador de terminal (Windows Terminal, etc.).
Então "fonte pequena" se resolve no terminal, não no opencode.

## Atalho rápido (para agora)

| Atalho | Efeito |
|---|---|
| `Ctrl+=` | Aumenta a fonte (zoom) |
| `Ctrl+-` | Diminui a fonte |
| `Ctrl+0` | Volta ao tamanho padrão |

O zoom com `Ctrl+=` vale só para a sessão atual do terminal.

## Ajuste permanente automático

O script `setup-display.py` detecta a tela (resolução, DPI, modelo do monitor)
e ajusta sozinho:

1. **Fonte do Windows Terminal** — grava `profiles.defaults.font.size` no `settings.json`.
2. **Layout do opencode** — ajusta `prompt.max_width/max_height` e `diff_style` no `~/.config/opencode/tui.json`.

### Como usar

```powershell
python ~/.config/opencode/scripts/setup-display.py --detect   # detecta e salva o perfil da tela
python ~/.config/opencode/scripts/setup-display.py --apply    # aplica fonte + layout
python ~/.config/opencode/scripts/setup-display.py --dry-run  # mostra o que faria, sem escrever
python ~/.config/opencode/scripts/setup-display.py --undo     # restaura os backups
```

### Como funciona

- `--detect` lê resolução, DPI e modelo do monitor e salva em
  `~/.config/opencode/state/display-profile.json`.
- `--apply` calcula a fonte recomendada a partir da altura da tela:

  | Altura (px) | Fonte |
  |---|---|
  | ≥ 2160 (4K) | 16pt |
  | ≥ 1440 (QHD) | 14pt |
  | < 2160 | 12pt (padrão) |

  Nunca reduz abaixo de 12pt. O Windows Terminal já escala por DPI sozinho,
  então o script não multiplica por escala de DPI.

- Antes de qualquer escrita o script cria backup `.bak` (o primeiro nunca é
  sobrescrito). `--undo` restaura.

## Se o script não for o suficiente

Edite a fonte manualmente no Windows Terminal:

1. Abra **Configurações** (`Ctrl+,`).
2. **Perfis** → seu perfil (ex.: Windows PowerShell) → **Aparência**.
3. Em **Tamanho da fonte**, escolha o valor (12 = padrão; 14–16 em telas grandes).

Ou edite direto o arquivo:
`%LOCALAPPDATA%\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json`

```json
{
  "profiles": {
    "defaults": {
      "font": { "size": 14, "face": "Cascadia Mono" }
    }
  }
}
```

O Windows Terminal recarrega esse arquivo ao vivo — sem reiniciar.

## Notas

- O `tui.json` do opencode é lido só na inicialização: após `--apply`, **reinicie
  o opencode** para o novo layout valer.
- O opencode não tem opção de fonte própria ainda — é um pedido em aberto no
  upstream (issue #9955). Por isso o ajuste acontece no terminal.
