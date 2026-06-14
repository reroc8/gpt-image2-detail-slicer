@echo off
chcp 65001 >nul
title 电商详情图切割AI高清化处理0.9

if not exist "%~dp0venv\Scripts\python.exe" (
    echo [错误] 请先运行 setup.bat 安装环境
    pause
    exit /b 1
)

call "%~dp0venv\Scripts\activate.bat"
python "%~dp0watch.py"
pause
