@echo off
setlocal

cd /d "%~dp0"

set PYTHON_EXE=D:\Anaconda\envs\denoising\python.exe

if not exist "%PYTHON_EXE%" (
  echo Could not find %PYTHON_EXE%
  echo Please edit start_backend.bat and set PYTHON_EXE to your Python path.
  pause
  exit /b 1
)

echo Installing/checking backend web dependencies...
"%PYTHON_EXE%" -m pip install fastapi "uvicorn[standard]" python-multipart pillow numpy

echo.
echo Starting Ray-Vision backend on http://127.0.0.1:8000
echo Press Ctrl+C to stop.
echo.
"%PYTHON_EXE%" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

endlocal
