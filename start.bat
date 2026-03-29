@echo off
chcp 65001 >nul
echo ========================================
echo   sjsZp Web - 启动应用
echo ========================================
echo.

echo [1/3] 启动 Flask 后端...
start "Flask Backend" cmd /k "cd /d %~dp0backend && C:\ProgramData\miniconda3\python.exe -m flask --app app run --port 5000 --debug"

timeout /t 3 /nobreak >nul

echo [2/3] 启动 React 前端...
start "React Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ========================================
echo   应用启动完成!
echo   前端：http://localhost:5173
echo   后端：http://localhost:5000
echo ========================================
echo.
echo 按任意键退出启动脚本...
pause >nul
