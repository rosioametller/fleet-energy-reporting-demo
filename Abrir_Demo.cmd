@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Falta el entorno virtual. Sigue la instalacion de README.md.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -E -B -c "import openpyxl, playwright"
if errorlevel 1 (
  echo Faltan dependencias. Instala requirements.txt dentro del entorno virtual.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -E -B -m fleet_lab.web --window
if errorlevel 1 (
  echo Revisa las instrucciones de Chromium y del puerto en README.md.
  pause
  exit /b 1
)
endlocal
