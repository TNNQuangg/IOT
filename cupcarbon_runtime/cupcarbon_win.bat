@echo off
cd /d "%~dp0"
java -Xmx2g -jar cupcarbon.jar %*
pause
