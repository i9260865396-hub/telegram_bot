@echo off
cd /d C:\telegram_bot

echo === Синхронизация проекта с GitHub ===

:: 1. Подтянуть последние изменения
echo.
echo --- Шаг 1: git pull ---
git pull origin main

:: 2. Добавить все локальные изменения
echo.
echo --- Шаг 2: git add ---
git add .

:: 3. Сделать коммит
echo.
echo --- Шаг 3: git commit ---
git commit -m "Автосинхронизация" || echo Нет изменений для коммита

:: 4. Подтянуть и объединить изменения с GitHub (rebase)
echo.
echo --- Шаг 4: git pull --rebase ---
git pull --rebase origin main

:: 5. Отправить всё обратно на GitHub
echo.
echo --- Шаг 5: git push ---
git push origin main

echo.
echo === ✅ Синхронизация завершена ===
pause
