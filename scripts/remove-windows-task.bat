@echo off
chcp 65001 >nul
title Remove MarkSix Auto Update Task
set "TASK_NAME=MarkSixAutoUpdate"

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Run as Administrator required.
    pause
    exit /b 1
)

schtasks /query /tn "%TASK_NAME%" >nul 2>&1
if %errorLevel% neq 0 (
    echo Task '%TASK_NAME%' does not exist.
    pause
    exit /b 0
)

echo Removing task: %TASK_NAME%
schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1
if %errorLevel% equ 0 (
    echo ✅ Task removed.
) else (
    echo ❌ Failed to remove task.
)
pause
