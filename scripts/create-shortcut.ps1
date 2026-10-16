# Creates a Start Menu shortcut "Panda Breath Control" (Windows).
#
#   powershell -ExecutionPolicy Bypass -File scripts\create-shortcut.ps1
#
# Uses pythonw.exe next to the first python.exe on PATH, so no console window
# opens. Run it again after moving the folder or changing Python.
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$launcher = Join-Path $root "panda-breath-control.pyw"
$icon = Join-Path $root "panda_breath_control\assets\icon.ico"

$python = (Get-Command python.exe -ErrorAction SilentlyContinue).Source
if (-not $python) { throw "python.exe was not found on PATH. Install Python 3.9 or newer first." }
$pythonw = Join-Path (Split-Path -Parent $python) "pythonw.exe"
if (-not (Test-Path $pythonw)) { throw "pythonw.exe was not found next to $python." }
# The Microsoft Store / scoop shims point elsewhere; ask Python where it really lives.
$real = & $python -c "import sys, os; print(os.path.join(os.path.dirname(sys.executable), 'pythonw.exe'))"
if (Test-Path $real) { $pythonw = $real }

$lnk = Join-Path ([Environment]::GetFolderPath("Programs")) "Panda Breath Control.lnk"
$shortcut = (New-Object -ComObject WScript.Shell).CreateShortcut($lnk)
$shortcut.TargetPath = $pythonw
$shortcut.Arguments = "`"$launcher`""
$shortcut.WorkingDirectory = $root
$shortcut.IconLocation = "$icon,0"
$shortcut.Description = "Panda Breath Control"
$shortcut.Save()
Write-Host "Created $lnk"
