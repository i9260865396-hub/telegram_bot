@echo off
title Telegram Print Bot (autoupdate + autolog)

:loop
echo [INFO] Проверяю обновления в GitHub...
cd /d C:\telegram_bot
git pull origin main

echo [INFO] Очищаю старый лог...
echo. > bot.log

echo [INFO] Запускаю бота...
.venv\Scripts\python.exe app.py >> bot.log 2>&1

echo [INFO] Бот завершился. Сохраняю лог в GitHub...
git add bot.log
git commit -m "update bot.log" >nul 2>&1
git push origin main

echo [INFO] Жду 5 секунд перед новым запуском...
timeout /t 5 >nul
goto loop
