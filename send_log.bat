@echo off
cd /d C:\telegram_bot

:: находим последний лог
for /f "delims=" %%F in ('dir /b /a-d /o-d logs\bot_*.log') do (
    set LASTLOG=logs\%%F
    goto found
)

:found
echo [1] Последний лог: %LASTLOG%

:: берём последние 200 строк
powershell -Command "Get-Content -Tail 200 '%LASTLOG%' | Set-Content 'logs\last_error.log'"

echo [2] Отправляем last_error.log в GitHub...
git add logs/last_error.log
git commit -m "log: обновлен last_error.log"
git push origin main

echo [✔] Лог успешно загружен в GitHub
pause
