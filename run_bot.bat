@echo off
@title BOREALIS2

echo Welcome to BOREALIS2. This will monitor the bot and make sure it gets restarted after crashes.
echo The bot will start in 60 seconds.
timeout 60

:START
cls
echo Bot started.
start /WAIT /MIN /NORMAL "" python run_borealis.py
cls
echo The bot has crashed.
echo Restarting in 60 seconds.
timeout 60

goto :START