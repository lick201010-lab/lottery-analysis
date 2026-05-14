#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Setup Windows Task Scheduler for automatic MarkSix data updates.
.DESCRIPTION
    Creates a scheduled task that runs update.py every Tue/Thu/Sat at 22:30
    (Hong Kong lottery draw nights, giving time for results to be published).
    Run this script as Administrator.
#>

$TaskName = "MarkSixAutoUpdate"
$ProjectDir = (Resolve-Path "$PSScriptRoot\..").Path
$PythonExe = "python"
$ScriptPath = "$ProjectDir\scripts\update.py"

# Verify script exists
if (-not (Test-Path $ScriptPath)) {
    Write-Error "Cannot find $ScriptPath"
    exit 1
}

# Remove old task if exists
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Removing existing task: $TaskName"
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Create the action
$Action = New-ScheduledTaskAction -Execute $PythonExe -Argument $ScriptPath -WorkingDirectory $ProjectDir

# Create the trigger: Tue, Thu, Sat at 22:30
# HK MarkSix draws are Tue/Thu/Sat ~21:30, we check at 22:30 to ensure results are published
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Tuesday, Thursday, Saturday -At "22:30"

# Create settings
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Register the task
Register-ScheduledTask -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Auto-update MarkSix lottery data from lottery.hk every draw night" `
    -Force

Write-Host ""
Write-Host "✅ Task '$TaskName' created successfully!"
Write-Host "   Schedule: Every Tuesday, Thursday, Saturday at 22:30"
Write-Host "   Command:  $PythonExe $ScriptPath"
Write-Host "   Work Dir: $ProjectDir"
Write-Host ""
Write-Host "You can manage this task in Task Scheduler (taskschd.msc)"
