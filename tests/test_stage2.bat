@echo off
cd /d "%~dp0.."
echo ##### Stage 2 tests #####
echo.
echo === no parameters ===
python src\emulator.py < tests\exit.txt
echo Exit code: %errorlevel%
echo.
echo === --vfs only ===
python src\emulator.py --vfs vfs\minimal.xml < tests\exit.txt
echo Exit code: %errorlevel%
echo.
echo === --script only ===
python src\emulator.py --script scripts\stage2.txt < tests\exit.txt
echo Exit code: %errorlevel%
echo.
echo === --vfs and --script ===
python src\emulator.py --vfs vfs\minimal.xml --script scripts\stage2.txt < tests\exit.txt
echo Exit code: %errorlevel%
echo.
echo === script with an error, must stop ===
python src\emulator.py --script scripts\error.txt < tests\exit.txt
echo Exit code: %errorlevel%
echo.
echo === script file does not exist ===
python src\emulator.py --script scripts\missing.txt < tests\exit.txt
echo Exit code: %errorlevel%
pause