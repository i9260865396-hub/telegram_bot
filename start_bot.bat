@echo off
cd /d C:\telegram_bot

:loop
echo ===============================
echo [GIT PULL] %date% %time%
git pull origin main
echo [BOT START] %date% %time%
echo ===============================

.\.venv\Scripts\python.exe app.py

echo [BOT STOPPED] %date% %time%
timeout /t 10 >nul
goto loop
