@echo off
setlocal
title Cancela Inteligente - INSTALACAO COMPLETA
cd /d "%~dp0"
echo.
echo ================================================================
echo   CANCELA INTELIGENTE - INSTALACAO COMPLETA
echo ================================================================
echo   Pasta: %CD%
echo.
echo   Primeira instalacao: precisa de internet e pode demorar.
echo   Em uma maquina ja preparada, o ambiente existente e reutilizado.
echo.
call "tools\python_runtime.bat" criar
if errorlevel 1 goto falha
"%CANCELA_ENV_PY%" "tools\preparar_projeto.py" instalar
if errorlevel 1 goto falha
echo.
echo ================================================================
echo   PROCESSO CONCLUIDO
echo   Para abrir o programa, execute iniciar.bat.
echo ================================================================
pause
exit /b 0
:falha
echo.
echo ================================================================
echo   NAO FOI POSSIVEL CONCLUIR
echo   Leia a primeira mensagem de erro acima.
echo   Registros de manutencao ficam na pasta outputs.
echo ================================================================
pause
exit /b 1
