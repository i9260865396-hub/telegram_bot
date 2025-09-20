@echo off
:loop
cd /d C:\telegram_bot
git pull origin main
.venv\Scripts\python.exe app.py
timeout /t 10
goto loop
