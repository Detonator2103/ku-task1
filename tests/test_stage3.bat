@echo off
cd /d "%~dp0.."
echo ##### Stage 3 tests #####
echo.
echo === minimal VFS ===
python src\emulator.py --vfs vfs\minimal.xml < tests\input_vfs_info.txt
echo Exit code: %errorlevel%
echo.
echo === several files VFS ===
python src\emulator.py --vfs vfs\several_files.xml < tests\input_vfs_info.txt
echo Exit code: %errorlevel%
echo.
echo === 3+ levels VFS with script ===
python src\emulator.py --vfs vfs\deep.xml --script scripts\stage3_all.txt < tests\exit.txt
echo Exit code: %errorlevel%
echo.
echo === VFS file not found ===
python src\emulator.py --vfs vfs\missing.xml < tests\exit.txt
echo Exit code: %errorlevel%
echo.
echo === broken XML ===
python src\emulator.py --vfs vfs\broken.xml < tests\exit.txt
echo Exit code: %errorlevel%
echo.
echo === errors in REPL ===
python src\emulator.py --vfs vfs\deep.xml < tests\input_errors_stage3.txt
echo Exit code: %errorlevel%
pause