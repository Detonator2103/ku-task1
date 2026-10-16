@echo off
cd /d "%~dp0.."
echo ##### Stage 1 tests #####
echo.
echo === REPL, input from file (with errors) ===
python src\emulator.py < tests\input_stage1.txt
echo Exit code: %errorlevel%
pause