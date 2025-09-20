@echo off
REM Автозапуск из Планировщика Windows — дергаем start_bot.bat из корня

cd /d "%~dp0"
start "" "%cd%\start_bot.bat"

pause