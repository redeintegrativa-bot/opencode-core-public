# OpenCode - Som de notificacao no terminal
# Uso: powershell -File play-sound.ps1 -Pattern <nome>
# Padroes: success | info | memory | warning | error | update | sync
# Gera tons (sine WAV 44.1k stereo) em memoria e toca via SoundPlayer -
# nao depende de console (funciona disparado escondido pelo plugin).
param(
    [Parameter(Mandatory = $true)][string]$Pattern
)

function Play-Tone($freq, $ms) {
    $samples = [int]($ms * 44100 / 1000)
    $stream = New-Object System.IO.MemoryStream
    $writer = New-Object System.IO.BinaryWriter($stream)
    $ascii = [System.Text.Encoding]::ASCII
    $writer.Write($ascii.GetBytes("RIFF"))
    $writer.Write([int32](36 + $samples * 4))
    $writer.Write($ascii.GetBytes("WAVE"))
    $writer.Write($ascii.GetBytes("fmt "))
    $writer.Write([int32]16)
    $writer.Write([int16]1)
    $writer.Write([int16]2)
    $writer.Write([int32]44100)
    $writer.Write([int32]176400)
    $writer.Write([int16]4)
    $writer.Write([int16]16)
    $writer.Write($ascii.GetBytes("data"))
    $writer.Write([int32]($samples * 4))
    for ($i = 0; $i -lt $samples; $i++) {
        $t = $i / 44100.0
        $v = [int]([math]::Sin(2 * [math]::PI * $freq * $t) * 0.25 * 32767)
        $writer.Write([int16]$v)
        $writer.Write([int16]$v)
    }
    $writer.Flush()
    $stream.Position = 0
    $player = New-Object System.Media.SoundPlayer($stream)
    $player.PlaySync()
    $player.Dispose()
    $writer.Dispose()
    $stream.Dispose()
}

switch ($Pattern) {
    "success" { Play-Tone 880 120; Start-Sleep -Milliseconds 50; Play-Tone 660 120 }
    "info"    { Play-Tone 784 150 }
    "memory"  { Play-Tone 784 120; Start-Sleep -Milliseconds 60; Play-Tone 1046 150 }
    "warning" { Play-Tone 440 160; Start-Sleep -Milliseconds 80; Play-Tone 440 160 }
    "error"   { Play-Tone 220 250; Start-Sleep -Milliseconds 60; Play-Tone 165 350 }
    "update"  { Play-Tone 988 130; Start-Sleep -Milliseconds 60; Play-Tone 1319 180 }
    "sync"    { Play-Tone 587 120; Start-Sleep -Milliseconds 60; Play-Tone 880 150 }
    default   { Play-Tone 660 120 }
}
