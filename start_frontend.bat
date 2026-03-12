@echo off
echo ============================================================
echo  MD-ADSS Frontend — Amazon Nova AI Hackathon
echo ============================================================

cd /d "%~dp0frontend"

:: Install npm deps if node_modules doesn't exist
if not exist node_modules (
    echo [1/2] Installing npm packages (first run — this takes ~30s)...
    npm install
)

:: Start Vite dev server
echo [2/2] Starting React dashboard on http://localhost:5173
echo.
npm run dev
