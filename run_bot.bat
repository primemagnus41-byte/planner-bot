@echo off
title PlannerBotWatcher
cd /d "D:\portfolio\startup\f ga\planner"

:loop
echo [%date% %time%] Bot ishga tushmoqda... >> data\bot.log
".venv\Scripts\python.exe" main.py >> data\bot.log 2>&1
echo [%date% %time%] Bot to'xtadi (kod: %errorlevel%). 5 soniyada qayta ishga tushadi... >> data\bot.log
timeout /t 5 /nobreak >nul
goto loop
