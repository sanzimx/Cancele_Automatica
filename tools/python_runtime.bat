@echo off
rem Rotina interna. Exporta CANCELA_ENV_PY para o batch chamador.
for %%I in ("%~dp0..") do set "CANCELA_PROJECT_ROOT=%%~fI"
set "CANCELA_ENV_PY=%CANCELA_PROJECT_ROOT%\.venv\Scripts\python.exe"
if exist "%CANCELA_ENV_PY%" goto validar
if /i not "%~1"=="criar" goto ambiente_ausente

set "CANCELA_SYS_PY="
for /f "delims=" %%P in ('py -3.11 -c "import sys; print(sys.executable)" 2^>nul') do if exist "%%P" set "CANCELA_SYS_PY=%%P"
if defined CANCELA_SYS_PY goto criar
echo Python 3.11 ausente. Instalando pelo gerenciador Python...
py install 3.11
for /f "delims=" %%P in ('py -3.11 -c "import sys; print(sys.executable)" 2^>nul') do if exist "%%P" set "CANCELA_SYS_PY=%%P"
if not defined CANCELA_SYS_PY goto python_ausente
:criar
echo Criando o ambiente do projeto...
"%CANCELA_SYS_PY%" -m venv "%CANCELA_PROJECT_ROOT%\.venv"
if errorlevel 1 exit /b 1
if not exist "%CANCELA_ENV_PY%" goto ambiente_ausente
:validar
"%CANCELA_ENV_PY%" -c "import sys; sys.exit(0 if sys.version_info[:2] == (3,11) else 1)"
if errorlevel 1 goto versao_incorreta
exit /b 0

:ambiente_ausente
echo Ambiente do projeto nao encontrado. Execute instalar.bat.
exit /b 1
:python_ausente
echo Nao foi possivel localizar Python 3.11.
echo Instale Python 3.11 com Tcl/Tk e o launcher py, depois tente novamente.
exit /b 1
:versao_incorreta
echo O ambiente existente nao usa Python 3.11. Ele foi preservado.
echo Nao remova o ambiente sem verificar suas dependencias e configuracoes.
exit /b 1
