# OpenCode - Som de notificacao no terminal (v4 - temas declarativos)
# Uso:
#   powershell -File play-sound.ps1 -Pattern <nome> [-Theme <nome>]
#       Padroes: success | info | memory | warning | error | update | sync
#   powershell -File play-sound.ps1 -ListThemes
#   powershell -File play-sound.ps1 -Preview [-Theme <nome>]
#   powershell -File play-sound.ps1 -SetTheme <nome>
#
# Os temas sao dados declarativos em $THEMES: cada padrao e uma lista de passos
# (note | chord | glide | silence) com timbre (wave), harmonicos, vibrato e
# decaimento. O tema ativo fica em ~/.config/opencode/state/sound-theme.txt e o
# plugin notify.js o le a cada chamada (troca sem reiniciar o opencode).
# Gera WAV 44.1k stereo em memoria (sem dependencias, sem arquivos de audio).

param(
    [Parameter(Mandatory = $false)][string]$Pattern = "",
    [string]$Theme = "",
    [switch]$ListThemes,
    [switch]$Preview,
    [string]$SetTheme = ""
)

$SR = 44100
$STATE_DIR = Join-Path $env:USERPROFILE ".config\opencode\state"
$STATE_FILE = Join-Path $STATE_DIR "sound-theme.txt"

# ---------------------------------------------------------------------------
# Motor de sintese (independente de tema)
# ---------------------------------------------------------------------------

function Get-WaveSample([double]$phase, $wave) {
    $p = $phase % (2 * [math]::PI)
    if ($p -lt 0) { $p += 2 * [math]::PI }
    switch ($wave) {
        'square'   { if ($p -lt [math]::PI) { return 1.0 } else { return -1.0 } }
        'triangle' {
            if ($p -lt [math]::PI) { return (2.0 * $p / [math]::PI - 1.0) } else { return (3.0 - 2.0 * $p / [math]::PI) }
        }
        'saw'      { return (2.0 * $p / (2.0 * [math]::PI) - 1.0) }
        default    { return [math]::Sin($p) }
    }
}

# Renderiza nota(s) em buffer: acorde = varios $freqs somados.
function Render-Tone([double[]]$freqs, $ms, $wave, $harmonics, $vibDepth, $vibRate, $decay) {
    if (-not $wave) { $wave = 'sine' }
    if ($null -eq $decay -or $decay -le 0) { $decay = 0.25 }
    if ($null -eq $vibDepth) { $vibDepth = 0.0 }
    if ($null -eq $vibRate) { $vibRate = 0.0 }
    if ($null -eq $harmonics) { $harmonics = @(@(1.0, 1.0)) }
    $n = [int]($ms * $SR / 1000)
    if ($n -lt 1) { return (New-Object 'double[]' 1) }
    $buf = New-Object 'double[]' $n
    $attack = [int]($n * 0.05)
    foreach ($base in $freqs) {
        $phase = 0.0
        for ($i = 0; $i -lt $n; $i++) {
            $t = $i / $SR
            $mod = 1.0 + $vibDepth * [math]::Sin(2 * [math]::PI * $vibRate * $t)
            $phase += 2 * [math]::PI * $base * $mod / $SR
            if ($wave -eq 'sine') {
                $v = 0.0
                foreach ($h in $harmonics) { $v += $h[1] * [math]::Sin($phase * $h[0]) }
            } else {
                $v = Get-WaveSample $phase $wave
            }
            $buf[$i] += $v
        }
    }
    $k = $freqs.Count
    for ($i = 0; $i -lt $n; $i++) {
        $t = $i / $SR
        $a = 1.0
        if ($i -lt $attack) { $a = $i / [double]$attack }
        $buf[$i] = ($buf[$i] / $k) * $a * [math]::Exp(-$t / $decay)
    }
    return $buf
}

# Portamento (glide) de f0 ate f1 por duracao (ms).
function Render-Glide($f0, $f1, $ms, $wave) {
    if (-not $wave) { $wave = 'sine' }
    $n = [int]($ms * $SR / 1000)
    if ($n -lt 1) { return (New-Object 'double[]' 1) }
    $buf = New-Object 'double[]' $n
    $attack = [int]($n * 0.05)
    $phase = 0.0
    for ($i = 0; $i -lt $n; $i++) {
        $t = $i / $SR
        $ratio = $i / [double]$n
        $f = $f0 + ($f1 - $f0) * $ratio
        $phase += 2 * [math]::PI * $f / $SR
        $v = Get-WaveSample $phase $wave
        $a = 1.0
        if ($i -lt $attack) { $a = $i / [double]$attack }
        $buf[$i] = $v * $a * [math]::Exp(-$t / 0.5)
    }
    return $buf
}

function Silence($ms) {
    return (New-Object 'double[]' ([int]($ms * $SR / 1000)))
}

# Adiciona eco (atraso + decaimento). Retorna buffer maior.
function Add-Echo($samples, $delayMs, $feedback, $repeats) {
    $delayN = [int]($delayMs * $SR / 1000)
    $total = $samples.Length + $delayN * $repeats
    $out = New-Object 'double[]' $total
    for ($i = 0; $i -lt $samples.Length; $i++) { $out[$i] += $samples[$i] }
    $amp = $feedback
    for ($r = 1; $r -le $repeats; $r++) {
        $off = $r * $delayN
        for ($i = 0; $i -lt $samples.Length; $i++) {
            $idx = $i + $off
            if ($idx -lt $total) { $out[$idx] += $samples[$i] * $amp }
        }
        $amp *= $feedback
    }
    return $out
}

function Concat([object[]]$parts) {
    $total = 0
    foreach ($p in $parts) { $total += $p.Length }
    $out = New-Object 'double[]' $total
    $pos = 0
    foreach ($p in $parts) {
        [Array]::Copy($p, 0, $out, $pos, $p.Length)
        $pos += $p.Length
    }
    return $out
}

# Renderiza um padrao declarativo (steps + echo) e normaliza o pico a 0.9.
function Render-Pattern($pattern) {
    $parts = @()
    foreach ($step in $pattern.steps) {
        switch ($step.type) {
            'silence' { $parts += Silence $step.ms }
            'note' {
                $harm = $step.harmonics
                if (-not $harm) { $harm = @(@(1.0, 1.0), @(2.0, 0.5), @(3.0, 0.25)) }
                $parts += Render-Tone @([double]$step.f) $step.ms $step.wave $harm $step.vib $step.vibrate $step.decay
            }
            'chord'  { $parts += Render-Tone @($step.freqs) $step.ms $step.wave $step.harmonics $step.vib $step.vibrate $step.decay }
            'glide'  { $parts += Render-Glide $step.f0 $step.f1 $step.ms $step.wave }
            default  { $parts += Silence 20 }
        }
    }
    $buf = Concat $parts
    if ($pattern.echo) {
        $buf = Add-Echo $buf $pattern.echo.delay $pattern.echo.feedback $pattern.echo.repeats
    }
    $peak = 0.0
    foreach ($s in $buf) { $a = [math]::Abs($s); if ($a -gt $peak) { $peak = $a } }
    if ($peak -gt 0.0001) {
        $scale = 0.9 / $peak
        for ($i = 0; $i -lt $buf.Length; $i++) { $buf[$i] = $buf[$i] * $scale }
    }
    return $buf
}

# Toca um buffer double[] como WAV stereo
function Play-Buffer($buf) {
    $n = $buf.Length
    $stream = New-Object System.IO.MemoryStream
    $writer = New-Object System.IO.BinaryWriter($stream)
    $ascii = [System.Text.Encoding]::ASCII
    $writer.Write($ascii.GetBytes("RIFF"))
    $writer.Write([int32](36 + $n * 4))
    $writer.Write($ascii.GetBytes("WAVE"))
    $writer.Write($ascii.GetBytes("fmt "))
    $writer.Write([int32]16)
    $writer.Write([int16]1)
    $writer.Write([int16]2)
    $writer.Write([int32]$SR)
    $writer.Write([int32]($SR * 4))
    $writer.Write([int16]4)
    $writer.Write([int16]16)
    $writer.Write($ascii.GetBytes("data"))
    $writer.Write([int32]($n * 4))
    for ($i = 0; $i -lt $n; $i++) {
        $s = [int]($buf[$i] * 0.5 * 32767)
        if ($s -gt 32767) { $s = 32767 }
        if ($s -lt -32767) { $s = -32767 }
        $writer.Write([int16]$s)
        $writer.Write([int16]$s)
    }
    $writer.Flush()
    $stream.Position = 0
    $player = New-Object System.Media.SoundPlayer($stream)
    $player.PlaySync()
    $player.Dispose()
    $writer.Dispose()
    $stream.Dispose()
}

# ---------------------------------------------------------------------------
# Temas declarativos
# ---------------------------------------------------------------------------
# Cada tema define os 7 padroes. Passos disponiveis:
#   note    -> f (Hz), ms, wave (sine|square|triangle|saw), harmonics @(@(mult,amp),...),
#              vib (profundidade), vibrate (Hz), decay (seg)
#   chord   -> freqs @(...) + mesmos params de note
#   glide   -> f0, f1, ms, wave
#   silence -> ms
# Padrao pode ter echo = @{ delay; feedback; repeats }.

# Timbres compartilhados entre temas (harmonicos: multiplicador, amplitude)
$WARM = @(@(1.0, 1.0), @(2.0, 0.45), @(3.0, 0.2))
$BELL = @(@(1.0, 1.0), @(1.5, 0.5), @(2.5, 0.3), @(3.7, 0.12))
$SOFT = @(@(1.0, 1.0), @(2.0, 0.3))

$THEMES = @{
  default = @{
    # brilho ascendente: arpejo C5-E5-G5-C6 + acorde maior final (victoria)
    success = @{
      steps = @(
        @{ type = 'note'; f = 523.25; ms = 110; decay = 0.12; harmonics = $WARM },
        @{ type = 'silence'; ms = 35 },
        @{ type = 'note'; f = 659.26; ms = 110; decay = 0.12; harmonics = $WARM },
        @{ type = 'silence'; ms = 35 },
        @{ type = 'note'; f = 783.99; ms = 110; decay = 0.12; harmonics = $WARM },
        @{ type = 'silence'; ms = 35 },
        @{ type = 'note'; f = 1046.50; ms = 140; decay = 0.16; harmonics = $WARM },
        @{ type = 'silence'; ms = 45 },
        @{ type = 'chord'; freqs = @(523.25, 659.26, 783.99); ms = 420; decay = 0.45; harmonics = $WARM }
      )
      echo = @{ delay = 170; feedback = 0.25; repeats = 2 }
    }
    # dois toques ascendentes (sininho metalico com eco)
    info = @{
      steps = @(
        @{ type = 'note'; f = 1046.50; ms = 170; decay = 0.18; harmonics = $BELL },
        @{ type = 'silence'; ms = 70 },
        @{ type = 'note'; f = 1318.51; ms = 300; decay = 0.3; harmonics = $BELL }
      )
      echo = @{ delay = 170; feedback = 0.22; repeats = 2 }
    }
    # subida suave e brilhante (memoria/checkpoint)
    memory = @{
      steps = @(
        @{ type = 'chord'; freqs = @(659.26, 830.61, 987.77); ms = 240; wave = 'triangle'; decay = 0.28 },
        @{ type = 'silence'; ms = 90 },
        @{ type = 'chord'; freqs = @(783.99, 987.77, 1174.66); ms = 340; wave = 'triangle'; decay = 0.35 }
      )
      echo = @{ delay = 180; feedback = 0.25; repeats = 2 }
    }
    # sirene acorde: agudo+grave alternando (estilo ambulancia) com presenca
    warning = @{
      steps = @(
        @{ type = 'chord'; freqs = @(880.00, 587.33); ms = 200; decay = 0.12 },
        @{ type = 'silence'; ms = 25 },
        @{ type = 'chord'; freqs = @(659.26, 440.00); ms = 200; decay = 0.12 },
        @{ type = 'silence'; ms = 25 },
        @{ type = 'chord'; freqs = @(880.00, 587.33); ms = 200; decay = 0.12 },
        @{ type = 'silence'; ms = 25 },
        @{ type = 'chord'; freqs = @(659.26, 440.00); ms = 200; decay = 0.12 },
        @{ type = 'silence'; ms = 25 },
        @{ type = 'chord'; freqs = @(880.00, 587.33); ms = 360; decay = 0.3 }
      )
      echo = @{ delay = 120; feedback = 0.15; repeats = 1 }
    }
    # queda lenta em cascata (falha): 3 degraus descendentes
    error = @{
      steps = @(
        @{ type = 'chord'; freqs = @(466.16, 440.00); ms = 300; decay = 0.28; harmonics = $SOFT },
        @{ type = 'silence'; ms = 80 },
        @{ type = 'chord'; freqs = @(392.00, 349.23); ms = 380; decay = 0.4; harmonics = $SOFT },
        @{ type = 'silence'; ms = 80 },
        @{ type = 'chord'; freqs = @(329.63, 293.66); ms = 420; decay = 0.45; harmonics = $SOFT }
      )
    }
    # cometa: glide com cauda estrelar (galaxia)
    update = @{
      steps = @(
        @{ type = 'glide'; f0 = 587.33; f1 = 1567.98; ms = 850 }
      )
      echo = @{ delay = 190; feedback = 0.32; repeats = 3 }
    }
    # data pulse: pacotes de dados subindo + handshake final (sync)
    sync = @{
      steps = @(
        @{ type = 'note'; f = 523.25; ms = 110; decay = 0.07; harmonics = $BELL },
        @{ type = 'silence'; ms = 30 },
        @{ type = 'note'; f = 587.33; ms = 110; decay = 0.07; harmonics = $BELL },
        @{ type = 'silence'; ms = 30 },
        @{ type = 'note'; f = 659.26; ms = 110; decay = 0.07; harmonics = $BELL },
        @{ type = 'silence'; ms = 30 },
        @{ type = 'note'; f = 783.99; ms = 110; decay = 0.07; harmonics = $BELL },
        @{ type = 'silence'; ms = 30 },
        @{ type = 'note'; f = 1046.50; ms = 200; decay = 0.14; harmonics = $BELL }
      )
      echo = @{ delay = 140; feedback = 0.3; repeats = 2 }
    }
  }

  # synthwave: saw detuned, glides estrelares e brilho ascendente
  neon = @{
    success = @{
      steps = @(
        @{ type = 'note'; f = 523.25; ms = 100; wave = 'saw'; decay = 0.12 },
        @{ type = 'silence'; ms = 50 },
        @{ type = 'note'; f = 659.26; ms = 100; wave = 'saw'; decay = 0.12 },
        @{ type = 'silence'; ms = 50 },
        @{ type = 'note'; f = 783.99; ms = 100; wave = 'saw'; decay = 0.12 },
        @{ type = 'silence'; ms = 50 },
        @{ type = 'chord'; freqs = @(523.25, 659.26, 783.99); ms = 380; wave = 'saw'; decay = 0.35 }
      )
      echo = @{ delay = 140; feedback = 0.25; repeats = 1 }
    }
    info = @{
      steps = @(
        @{ type = 'note'; f = 880.00; ms = 180; vib = 0.004; vibrate = 6; decay = 0.2 },
        @{ type = 'silence'; ms = 60 },
        @{ type = 'note'; f = 1318.51; ms = 300; vib = 0.004; vibrate = 6; decay = 0.28 }
      )
      echo = @{ delay = 160; feedback = 0.2; repeats = 1 }
    }
    memory = @{
      steps = @(
        @{ type = 'chord'; freqs = @(659.26, 830.61, 987.77); ms = 220; wave = 'triangle'; decay = 0.25 },
        @{ type = 'silence'; ms = 80 },
        @{ type = 'chord'; freqs = @(783.99, 987.77, 1174.66); ms = 300; wave = 'triangle'; decay = 0.3 }
      )
    }
    # alarme ascendente (perigo) + acorde final
    warning = @{
      steps = @(
        @{ type = 'glide'; f0 = 261.63; f1 = 523.25; ms = 350; wave = 'saw' },
        @{ type = 'silence'; ms = 40 },
        @{ type = 'glide'; f0 = 261.63; f1 = 523.25; ms = 350; wave = 'saw' },
        @{ type = 'silence'; ms = 40 },
        @{ type = 'chord'; freqs = @(440.00, 587.33); ms = 400; wave = 'saw'; decay = 0.25 }
      )
    }
    error = @{
      steps = @(
        @{ type = 'glide'; f0 = 392.00; f1 = 196.00; ms = 420; wave = 'saw' },
        @{ type = 'silence'; ms = 80 },
        @{ type = 'chord'; freqs = @(220.00, 261.63, 329.63); ms = 460; wave = 'saw'; decay = 0.35 }
      )
    }
    update = @{
      steps = @(
        @{ type = 'glide'; f0 = 440.00; f1 = 1567.98; ms = 820; wave = 'saw' }
      )
      echo = @{ delay = 200; feedback = 0.35; repeats = 2 }
    }
    sync = @{
      steps = @(
        @{ type = 'note'; f = 587.33; ms = 90; wave = 'saw'; decay = 0.08 },
        @{ type = 'silence'; ms = 35 },
        @{ type = 'note'; f = 659.26; ms = 90; wave = 'saw'; decay = 0.08 },
        @{ type = 'silence'; ms = 35 },
        @{ type = 'note'; f = 783.99; ms = 90; wave = 'saw'; decay = 0.08 },
        @{ type = 'silence'; ms = 35 },
        @{ type = 'note'; f = 1046.50; ms = 90; wave = 'saw'; decay = 0.08 },
        @{ type = 'silence'; ms = 35 },
        @{ type = 'note'; f = 1318.51; ms = 180; wave = 'saw'; decay = 0.15 }
      )
      echo = @{ delay = 130; feedback = 0.3; repeats = 2 }
    }
  }

  # 8-bit: square/triangle puros, arpejos e moeda/powerup
  retro = @{
    success = @{
      steps = @(
        @{ type = 'note'; f = 523.25; ms = 70; wave = 'square'; decay = 0.07 },
        @{ type = 'silence'; ms = 20 },
        @{ type = 'note'; f = 659.26; ms = 70; wave = 'square'; decay = 0.07 },
        @{ type = 'silence'; ms = 20 },
        @{ type = 'note'; f = 783.99; ms = 70; wave = 'square'; decay = 0.07 },
        @{ type = 'silence'; ms = 20 },
        @{ type = 'note'; f = 1046.50; ms = 220; wave = 'square'; decay = 0.2 }
      )
    }
    info = @{
      steps = @(
        @{ type = 'note'; f = 1046.50; ms = 160; wave = 'square'; decay = 0.15 },
        @{ type = 'silence'; ms = 40 },
        @{ type = 'note'; f = 1318.51; ms = 200; wave = 'square'; decay = 0.2 }
      )
    }
    # powerup ascendente
    memory = @{
      steps = @(
        @{ type = 'note'; f = 392.00; ms = 90; wave = 'triangle'; decay = 0.09 },
        @{ type = 'silence'; ms = 25 },
        @{ type = 'note'; f = 523.25; ms = 90; wave = 'triangle'; decay = 0.09 },
        @{ type = 'silence'; ms = 25 },
        @{ type = 'note'; f = 659.26; ms = 90; wave = 'triangle'; decay = 0.09 },
        @{ type = 'silence'; ms = 25 },
        @{ type = 'note'; f = 783.99; ms = 120; wave = 'triangle'; decay = 0.12 },
        @{ type = 'silence'; ms = 25 },
        @{ type = 'note'; f = 1046.50; ms = 200; wave = 'triangle'; decay = 0.18 }
      )
    }
    warning = @{
      steps = @(
        @{ type = 'note'; f = 880.00; ms = 200; wave = 'square'; decay = 0.15 },
        @{ type = 'silence'; ms = 30 },
        @{ type = 'note'; f = 659.26; ms = 200; wave = 'square'; decay = 0.15 },
        @{ type = 'silence'; ms = 30 },
        @{ type = 'note'; f = 880.00; ms = 200; wave = 'square'; decay = 0.15 },
        @{ type = 'silence'; ms = 30 },
        @{ type = 'note'; f = 659.26; ms = 200; wave = 'square'; decay = 0.15 },
        @{ type = 'silence'; ms = 30 },
        @{ type = 'note'; f = 880.00; ms = 360; wave = 'square'; decay = 0.3 }
      )
    }
    error = @{
      steps = @(
        @{ type = 'glide'; f0 = 523.25; f1 = 130.81; ms = 450; wave = 'square' },
        @{ type = 'silence'; ms = 60 },
        @{ type = 'note'; f = 130.81; ms = 320; wave = 'square'; decay = 0.3 }
      )
    }
    update = @{
      steps = @(
        @{ type = 'glide'; f0 = 587.33; f1 = 1174.66; ms = 200; wave = 'square' },
        @{ type = 'silence'; ms = 30 },
        @{ type = 'glide'; f0 = 783.99; f1 = 1567.98; ms = 300; wave = 'square' }
      )
    }
    sync = @{
      steps = @(
        @{ type = 'note'; f = 659.26; ms = 80; wave = 'square'; decay = 0.06 },
        @{ type = 'silence'; ms = 30 },
        @{ type = 'note'; f = 783.99; ms = 80; wave = 'square'; decay = 0.06 },
        @{ type = 'silence'; ms = 30 },
        @{ type = 'note'; f = 659.26; ms = 80; wave = 'square'; decay = 0.06 },
        @{ type = 'silence'; ms = 30 },
        @{ type = 'note'; f = 783.99; ms = 80; wave = 'square'; decay = 0.06 },
        @{ type = 'silence'; ms = 30 },
        @{ type = 'note'; f = 1046.50; ms = 160; wave = 'square'; decay = 0.12 }
      )
    }
  }
}

# ---------------------------------------------------------------------------
# Comandos
# ---------------------------------------------------------------------------

if ($ListThemes) {
    Write-Output ("Temas disponiveis: " + (($THEMES.Keys | Sort-Object) -join ', '))
    exit 0
}

if ($SetTheme) {
    if (-not $THEMES.ContainsKey($SetTheme)) {
        Write-Output ("Tema desconhecido: {0}. Disponiveis: {1}" -f $SetTheme, (($THEMES.Keys | Sort-Object) -join ', '))
        exit 1
    }
    if (-not (Test-Path $STATE_DIR)) { New-Item -ItemType Directory -Path $STATE_DIR -Force | Out-Null }
    Set-Content -Path $STATE_FILE -Value $SetTheme -Encoding ascii -NoNewline
    Write-Output ("Tema ativo: {0}" -f $SetTheme)
    exit 0
}

if (-not $Theme) {
    $Theme = if (Test-Path $STATE_FILE) { (Get-Content $STATE_FILE -Raw).Trim() } else { 'default' }
}
if (-not $THEMES.ContainsKey($Theme)) { $Theme = 'default' }

if ($Preview) {
    foreach ($n in @('success', 'info', 'memory', 'warning', 'error', 'update', 'sync')) {
        Write-Output ("[preview] {0}.{1}" -f $Theme, $n)
        Play-Buffer (Render-Pattern $THEMES[$Theme][$n])
        Start-Sleep -Milliseconds 250
    }
    exit 0
}

if (-not $Pattern) {
    Write-Output "Uso: -Pattern <nome> [-Theme <nome>] | -ListThemes | -Preview [-Theme <nome>] | -SetTheme <nome>"
    exit 1
}

if ($THEMES[$Theme].ContainsKey($Pattern)) {
    Play-Buffer (Render-Pattern $THEMES[$Theme][$Pattern])
} else {
    Play-Buffer (Render-Pattern $THEMES[$Theme]['info'])
}
