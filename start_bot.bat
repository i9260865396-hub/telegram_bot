@echo off
setlocal
title Telegram Print Bot - Start

REM Переходим в текущую папку, где лежит батник (корень проекта)
cd /d %~dp0

IF NOT EXIST .venv (
  echo [ERR] No venv found. Run install_deps_once.bat first.
  pause
  exit /b 1
)

IF NOT EXIST .env (
  echo [ERR] .env not found in %cd%\.env
  pause
  exit /b 1
)

IF NOT EXIST logs mkdir logs
set PYTHONUTF8=1

REM Логи в файл уже пишет сам бот (logs\bot.log). Просто запускаем.
.\.venv\Scripts\python.exe app.py

echo.
echo [INFO] Bot process finished (check logs\bot.log for details).
pause
