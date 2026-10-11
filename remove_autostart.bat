@echo off
chcp 65001 >nul
echo 🗑 Avto-yuklash o'chirilmoqda...
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\PlannerBot.lnk" 2>nul
echo.
echo ✅ Avto-yuklash o'chirildi!
echo.
pause
