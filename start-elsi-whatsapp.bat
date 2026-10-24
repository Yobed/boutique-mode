@echo off
title ELSI - Service Client WhatsApp IA (+225 05 74 24 37 52)
cd /d "%~dp0"
echo =====================================================================
echo   MAISON ELSI - SERVICE CLIENT WHATSAPP CONVERSATIONNEL IA
echo   Numero officiel : +225 05 74 24 37 52
echo   Dashboard local : http://localhost:5690
echo =====================================================================
echo.
node services/elsi-whatsapp-bot/server.js
pause
