@echo off
chcp 65001 >nul
title GPT Image 2 详情图切列高清器 0.9 - 安装

echo ============================================
echo   GPT Image 2 详情图切列高清器 0.9
echo   内部使用 请勿外传
echo ============================================
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python
    echo 请安装 Python 3.14:
    echo   https://www.python.org/downloads/
    echo 安装时务必勾选 "Add Python to PATH"
    pause
    exit /b 1
)

python -c "import sys; sys.exit(0 if sys.version_info[:2] == (3,14) else 1)"
if %errorlevel% neq 0 (
    echo [错误] 需要 Python 3.14，当前版本不符
    pause
    exit /b 1
)

python --version
echo.

if not exist "%~dp0venv" (
    echo [1/3] 创建虚拟环境...
    python -m venv "%~dp0venv"
    if %errorlevel% neq 0 (
        echo [错误] 创建失败
        pause
        exit /b 1
    )
) else (
    echo [1/3] 检查虚拟环境...
    "%~dp0venv\Scripts\python.exe" -c "import sys; sys.exit(0 if sys.version_info[:2]==(3,14) else 1)"
    if %errorlevel% neq 0 (
        echo   版本不符，重建中...
        rmdir /s /q "%~dp0venv"
        python -m venv "%~dp0venv"
        if %errorlevel% neq 0 (
            echo [错误] 重建失败
            pause
            exit /b 1
        )
    ) else (
        echo   已就绪
    )
)

echo.
call "%~dp0venv\Scripts\activate.bat"

echo [2/3] 安装所有依赖（本地文件，无需联网）...

pip install --no-index --find-links="%~dp0wheels" torch torchvision opencv-python-headless tqdm addict future lmdb Pillow pyyaml requests scikit-image scipy
if %errorlevel% neq 0 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

echo.
echo [3/3] 安装 basicsr + realesrgan...
pip install --no-deps "%~dp0wheels\basicsr-fix.zip"
if %errorlevel% neq 0 (
    echo [错误] basicsr 安装失败
    pause
    exit /b 1
)

pip install --no-index --find-links="%~dp0wheels" --no-deps realesrgan
if %errorlevel% neq 0 (
    echo [错误] realesrgan 安装失败
    pause
    exit /b 1
)

echo.
echo ============================================
echo   安装完成
echo.
echo   双击 "开始处理.bat" 启动
echo   拖图片到 放入图片\ 即可自动处理
echo ============================================
pause
