@echo off
echo Planner bot to'xtatilmoqda...
powershell -NoProfile -Command "$p = Get-CimInstance Win32_Process -Filter \"Name = 'python.exe'\"; foreach ($x in $p) { if ($x.CommandLine -match 'planner.+main\.py') { Stop-Process -Id $x.ProcessId -Force; Write-Host 'To''xtatildi PID:' $x.ProcessId } }"
echo.
echo [OK] Bot to'xtatildi!
pause
