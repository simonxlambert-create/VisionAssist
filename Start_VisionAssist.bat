@echo off
title VisionAssist - Low Vision Cursor Helper
cd /d "%~dp0"
echo =======================================================
echo VisionAssist is active!
echo.
echo Active Shortcuts (Belgian AZERTY + Standard):
echo   * F8  (or Ctrl + *) : Instant High-Visibility RED Cursor
echo   * F9  (or Ctrl + /) : Instant Cursor Size (32px / 64px / 96px)
echo   * Single Tap Ctrl   : Glowing Animated RED Radar Circles!
echo.
echo (Keep this window minimized while in use)
echo =======================================================
echo.
"C:\Users\simon\AppData\Local\Programs\Python\Python313\python.exe" main.py
pause
