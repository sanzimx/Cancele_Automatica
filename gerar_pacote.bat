@echo off
setlocal
title Cancela Inteligente - Pacote de Instalacao
cd /d "%~dp0"
echo ================================================================
echo   CANCELA INTELIGENTE - GERAR PACOTE PARA OUTRA MAQUINA
echo ================================================================
call "tools\python_runtime.bat"
if errorlevel 1 goto falha
"%CANCELA_ENV_PY%" tools\empacotar.py
if errorlevel 1 goto falha
echo.
echo Pacote disponivel em dist\Cancela_Inteligente_Instalacao.zip
pause
exit /b 0
:falha
echo Falha ao gerar o pacote. Leia a mensagem acima.
pause
exit /b 1
