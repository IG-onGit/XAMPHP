@echo off

:: Check if running with admin rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "Start-Process '%~f0' -ArgumentList '%*' -Verb RunAs" 2>nul
    exit /b
)

:: Get arguments
set target_file=%1
set temp_file=%2

:: Check if both files exist
if not exist "%target_file%" call :deleteTemp "Target file not found"
if not exist "%temp_file%"  call :deleteTemp "Temp file not found"

:: Copy content from temp file to target file
copy /Y "%temp_file%" "%target_file%" >nul
if %errorlevel% neq 0 (
    call :deleteTemp "Error during copy"
    exit /b 1
)

:: Always delete temp file at the end
call :deleteTemp "Cleanup at end"
exit /b

:: Function to delete temp file
:deleteTemp
set "hint=%~1"
echo %hint%
if exist "%temp_file%" del "%temp_file%"
exit /b
