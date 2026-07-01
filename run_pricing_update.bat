@echo off
setlocal

REM Run from the folder this .bat file lives in
cd /d "%~dp0"

echo === Running pricing update ===
python update_pricing.py
set PY_EXIT=%ERRORLEVEL%

if %PY_EXIT%==2 (
    echo No new pricing data to commit. Done.
    goto :end
)

if %PY_EXIT%==1 (
    echo update_pricing.py reported an error. Skipping git commit/push.
    goto :end
)

if not %PY_EXIT%==0 (
    echo Unexpected exit code %PY_EXIT% from update_pricing.py. Skipping git commit/push.
    goto :end
)

echo === Committing and pushing changes ===
git add .
git commit -m "updated pricing"
git push

:end
echo.
pause
