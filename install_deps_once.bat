@echo off
setlocal enabledelayedexpansion
title Telegram Print Bot - Install

REM Остаёмся в корне проекта
cd /d %~dp0

IF NOT EXIST .venv (
  py -3 -m venv .venv
)

CALL .\.venv\Scripts\python.exe -m pip install --upgrade pip
CALL .\.venv\Scripts\pip.exe install ^
  "aiogram>=3.20,<3.23" ^
  "aiohttp>=3.12,<3.13" ^
  "pydantic>=2.11,<2.12" ^
  pydantic-settings ^
  python-dotenv ^
  "SQLAlchemy>=2.0,<2.1" ^
  "alembic>=1.13,<1.15" ^
  "tzdata" ^
  "aiosqlite>=0.20,<0.21" ^
  "greenlet>=3.0,<4.0"

echo.
echo [OK] Venv: %cd%\.venv
echo [OK] Dependencies installed.
pause
