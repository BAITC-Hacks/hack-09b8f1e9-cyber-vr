@echo off
cd /d "%~dp0"
if not exist .venv (py -m venv .venv || exit /b 1)
call .venv\Scripts\activate.bat
python -m pip install -r requirements.txt || exit /b 1
if not exist .env (copy .env.example .env & echo Add a NEW key to .env, then run again. & pause & exit /b 0)
start http://127.0.0.1:5000
python app.py
pause
