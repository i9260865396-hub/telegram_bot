@echo off
cd /d C:\telegram_bot

if not exist logs mkdir logs

:loop
echo [1] Проверка обновлений с GitHub...
git pull origin main

:: Создаём уникальный лог с датой и временем
set LOGFILE=logs\bot_%DATE:~6,4%-%DATE:~3,2%-%DATE:~0,2%_%TIME:~0,2%-%TIME:~3,2%-%TIME:~6,2%.log
set LOGFILE=%LOGFILE: =0%

echo [2] Запуск бота, лог пишется в %LOGFILE% ...
.\.venv\Scripts\python.exe app.py *>> %LOGFILE% 2>&1

echo [3] Чистим старые логи, оставляем только 5 последних...
for /f "skip=5 delims=" %%F in ('dir /b /a-d /o-d logs\bot_*.log') do del "logs\%%F"

echo [!] Бот упал. Перезапуск через 5 секунд...
timeout /t 5
goto loop
