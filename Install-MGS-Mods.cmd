@echo off
setlocal
title MGS Master Collection Mod Kit
set "TAG=v2.0.1"
set "SHA=4a308fcc88cb968cc9ba48ae829e3eb089971135df27b09c4ac53603ff76719c"
set "URL=https://github.com/cntrl-alt-lenny/mgs-mc-modkit/releases/download/%TAG%/install.py"
set "F=%TEMP%\mgs_install_%RANDOM%%RANDOM%.py"
echo Fetching the MGS Mod Kit installer (%TAG%)...
curl -fsSL "%URL%" -o "%F%"
if errorlevel 1 goto fail
rem Verify the download against the pinned SHA-256 before running anything.
for /f "usebackq delims=" %%H in (`powershell -NoProfile -Command "(Get-FileHash -Algorithm SHA256 -LiteralPath '%F%').Hash.ToLower()"`) do set "GOT=%%H"
if /i not "%GOT%"=="%SHA%" goto fail
where py >nul 2>nul
if not errorlevel 1 goto runpy
where python >nul 2>nul
if errorlevel 1 goto nopython
python "%F%"
if errorlevel 9009 goto nopython
goto cleanup
:runpy
py -3 "%F%"
goto cleanup
:nopython
echo.
echo Python is needed to run the installer and was not found.
echo Install it free from python.org - IMPORTANT: tick "Add python.exe to PATH" -
echo then double-click this file again.
start https://www.python.org/downloads/
goto cleanup
:fail
echo.
echo Could not download or verify the installer. Nothing was changed.
echo Check your internet connection and try again.
:cleanup
if exist "%F%" del /q "%F%" >nul 2>nul
echo.
pause
