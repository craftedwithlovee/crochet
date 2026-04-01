@echo off
echo Restarting PostgreSQL service...
net stop postgresql-x64-18
timeout /t 3
net start postgresql-x64-18
echo.
echo PostgreSQL restarted!
pause
