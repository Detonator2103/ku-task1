@echo off
cd /d "%~dp0.."
echo ##### Stage 5 tests #####
echo.
echo === chmod and touch in a script ===
python src\emulator.py --vfs vfs\deep.xml --script scripts\stage5_all.txt < tests\exit.txt
echo Exit code: %errorlevel%
echo.
echo === errors in REPL ===
python src\emulator.py --vfs vfs\deep.xml < tests\input_errors_stage5.txt
echo Exit code: %errorlevel%
pause