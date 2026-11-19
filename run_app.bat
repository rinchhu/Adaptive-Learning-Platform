@echo off
title Adaptive Learning Platform
cd /d "%~dp0"
python main.py
if %errorlevel% neq 0 (
    echo.
    echo An error occurred while launching the application.
    pause
)
