# OpenCode - Toast do Windows (silencioso)
# Uso: powershell -File windows-toast.ps1 -Title "..." -Message "..."
# Silencioso de proposito: o som de notificacao fica no terminal (play-sound.ps1).
param(
    [Parameter(Mandatory = $true)][string]$Title,
    [Parameter(Mandatory = $true)][string]$Message,
    [string]$AppId = "OpenCode"
)

try {
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
    [Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
    [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

    $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
    $textNodes = $template.GetElementsByTagName("text")
    $textNodes.Item(0).AppendChild($template.CreateTextNode($Title)) | Out-Null
    $textNodes.Item(1).AppendChild($template.CreateTextNode($Message)) | Out-Null

    $audio = $template.SelectSingleNode("//audio")
    if ($audio) {
        $audio.SetAttribute("silent", "true")
    } else {
        $newAudio = $template.CreateElement("audio")
        $newAudio.SetAttribute("silent", "true")
        $template.DocumentElement.AppendChild($newAudio) | Out-Null
    }

    $toast = [Windows.UI.Notifications.ToastNotification]::new($template)
    $notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($AppId)
    $notifier.Show($toast)
    exit 0
} catch {
    # Fallback: balloon do sistema (funciona sem suporte a toast UWP)
    try {
        Add-Type -AssemblyName System.Windows.Forms | Out-Null
        Add-Type -AssemblyName System.Drawing | Out-Null
        $balloon = New-Object System.Windows.Forms.NotifyIcon
        $balloon.Icon = [System.Drawing.SystemIcons]::Information
        $balloon.BalloonTipTitle = $Title
        $balloon.BalloonTipText = $Message
        $balloon.Visible = $true
        $balloon.ShowBalloonTip(8000)
        Start-Sleep -Seconds 2
        $balloon.Dispose()
        exit 0
    } catch {
        exit 1
    }
}
