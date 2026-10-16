@echo off
cd /d "%~dp0.."
echo ##### Stage 4 tests #####
echo.
echo === all stage 4 commands in a script ===
python src\emulator.py --vfs vfs\deep.xml --script scripts\stage4_all.txt < tests\exit.txt
echo Exit code: %errorlevel%
echo.
echo === errors in REPL ===
python src\emulator.py --vfs vfs\deep.xml < tests\input_errors_stage4.txt
echo Exit code: %errorlevel%
pause