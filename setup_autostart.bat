@echo off
chcp 65001 >nul
echo 🔄 Windows Startup (Avto-yuklash) sozlanmoqda...

set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "TARGET_VBS=D:\portfolio\startup\f ga\planner\start_bot_silent.vbs"

powershell -NoProfile -Command ^
  "$ws = New-Object -ComObject WScript.Shell; " ^
  "$s = $ws.CreateShortcut('%STARTUP_DIR%\PlannerBot.lnk'); " ^
  "$s.TargetPath = 'wscript.exe'; " ^
  "$s.Arguments = '\"%TARGET_VBS%\"'; " ^
  "$s.WorkingDirectory = 'D:\portfolio\startup\f ga\planner'; " ^
  "$s.WindowStyle = 7; " ^
  "$s.Save()"

echo.
echo ✅ Muvaffaqiyatli sozlandi!
echo Endi kompyuter har safar yoqilganda bot avtomatik fonda ishga tushadi.
echo.
pause
