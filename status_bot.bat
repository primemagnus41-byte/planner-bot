@echo off
powershell -NoProfile -Command "$p = Get-CimInstance Win32_Process -Filter \"Name = 'python.exe'\"; $found = $false; foreach ($x in $p) { if ($x.CommandLine -match 'planner.+main\.py') { Write-Host ' [32m[OK] Bot ISHLAYAPTI! PID: ' $x.ProcessId ' [0m'; $found = $true } }; if (-not $found) { Write-Host ' [31m[!] Bot TO''XTATILGAN (Ishlamayapti) [0m' }"
pause
