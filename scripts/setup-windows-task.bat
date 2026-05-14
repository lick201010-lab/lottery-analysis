@echo off
chcp 65001 >nul
title Setup MarkSix Auto Update Task
echo ==========================================
echo  MarkSix Windows Auto-Update Setup
echo ==========================================
echo.

:: Check for admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ This script must be run as Administrator.
    echo    Right-click this file and select "Run as administrator".
    pause
    exit /b 1
)

set "TASK_NAME=MarkSixAutoUpdate"
set "PROJECT_DIR=%~dp0.."
set "SCRIPT_PATH=%PROJECT_DIR%\scripts\update.py"

if not exist "%SCRIPT_PATH%" (
    echo ❌ Cannot find: %SCRIPT_PATH%
    pause
    exit /b 1
)

:: Remove existing task
schtasks /query /tn "%TASK_NAME%" >nul 2>&1
if %errorLevel% equ 0 (
    echo Removing existing task: %TASK_NAME%
    schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1
)

:: Create new task - Tue, Thu, Sat at 22:30
echo Creating scheduled task: %TASK_NAME%
schtasks /create /tn "%TASK_NAME%" ^
    /tr "python \"%SCRIPT_PATH%\"" ^
    /sc weekly ^
    /d TUE,THU,SAT ^
    /st 22:30 ^
    /rl highest ^
    /f >nul 2>&1

if %errorLevel% neq 0 (
    echo ❌ Failed to create task.
    pause
    exit /b 1
)

echo.
echo ✅ Task '%TASK_NAME%' created successfully!
echo    Schedule: Every Tuesday, Thursday, Saturday at 22:30
echo    Script:   %SCRIPT_PATH%
echo.
echo You can manage this task in Task Scheduler (taskschd.msc)
echo.
pause
