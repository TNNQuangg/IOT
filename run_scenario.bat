@echo off
setlocal
chcp 65001 >nul
pushd "%~dp0" || exit /b 1
where python >nul 2>&1
if errorlevel 1 (
    py -3 run_cupcarbon.py %*
) else (
    python run_cupcarbon.py %*
)
set "run_status=%ERRORLEVEL%"
popd
exit /b %run_status%
