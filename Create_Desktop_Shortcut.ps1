$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$target = Join-Path $root "Run_Sonic_Cipher.bat"
$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "Sonic Cipher.lnk"

$wsh = New-Object -ComObject WScript.Shell
$shortcut = $wsh.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $target
$shortcut.WorkingDirectory = $root
$shortcut.IconLocation = "$env:SystemRoot\System32\shell32.dll,133"
$shortcut.Save()

Write-Host "Shortcut created at $shortcutPath"
