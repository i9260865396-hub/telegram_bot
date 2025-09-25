@echo off
echo === 🚀 Синхронизация проекта с GitHub ===

:: Шаг 1. Проверяем статус
git status

:: Шаг 2. Добавляем все изменения
echo --- Добавляем файлы ---
git add .

:: Шаг 3. Делаем коммит (если есть изменения)
echo --- Делаем коммит ---
git commit -m "Auto-sync: обновление кода (Service, init_db, admin)" || echo Нет изменений для коммита

:: Шаг 4. Подтягиваем свежий main с GitHub
echo --- Подтягиваем обновления с GitHub ---
git pull --rebase origin main

:: Шаг 5. Отправляем изменения на GitHub
echo --- Отправляем изменения ---
git push origin main

echo === ✅ Синхронизация завершена ===
pause
