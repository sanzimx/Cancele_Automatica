@echo off
setlocal
title Cancela Inteligente
cd /d "%~dp0"
call "tools\python_runtime.bat"
if errorlevel 1 goto falha
"%CANCELA_ENV_PY%" tools\organizar_projeto.py
if errorlevel 1 goto falha
echo Abrindo a Cancela Inteligente...
echo Mantenha esta janela aberta enquanto usa o programa.
"%CANCELA_ENV_PY%" -X faulthandler app.py
set "CANCELA_EXIT_CODE=%ERRORLEVEL%"
if "%CANCELA_EXIT_CODE%"=="0" exit /b 0
echo O programa encerrou com codigo %CANCELA_EXIT_CODE%.
:falha
echo.
echo Nao foi possivel abrir ou manter o programa em execucao.
echo Copie a mensagem acima. Diagnosticos do OCR ficam em outputs.
pause
exit /b 1
