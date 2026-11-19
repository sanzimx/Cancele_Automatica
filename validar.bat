@echo off
setlocal
title Cancela Inteligente - VERIFICAR INSTALACAO
cd /d "%~dp0"
echo.
echo ================================================================
echo   CANCELA INTELIGENTE - VERIFICAR INSTALACAO
echo ================================================================
echo   Pasta: %CD%
echo.
echo   Feche a interface antes de executar esta manutencao.
echo.
call "tools\python_runtime.bat"
if errorlevel 1 goto falha
"%CANCELA_ENV_PY%" "tools\preparar_projeto.py" validar
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
