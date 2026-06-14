#!/bin/bash
set -o pipefail
cd "$(dirname "$0")"
echo "============================================"
echo "  GPT Image 2 详情图切列高清器 安装"
echo "============================================"
echo ""

# 检查 Python
python3 --version 2>/dev/null || { echo "[错误] 请先安装 Python 3"; exit 1; }

# 检查依赖
echo "检查依赖..."
python3 -c "import cv2, torch, numpy, realesrgan, torchvision, tqdm, basicsr.archs.rrdbnet_arch" 2>/dev/null && echo "依赖已就绪" || {
    echo "缺少依赖，正在安装..."
    PY=$(dirname "$(which python3)")
    PIP="$PY/pip3"

    echo "  [1/3] torch + torchvision..."
    $PIP install torch torchvision opencv-python-headless tqdm realesrgan 2>&1 | tail -3
    if [ $? -ne 0 ]; then echo "[错误] 安装失败，请检查网络或权限"; exit 1; fi

    echo "  [2/3] basicsr..."
    $PIP install https://github.com/Disty0/BasicSR/archive/refs/heads/master.zip 2>&1 | tail -3
    if [ $? -ne 0 ]; then echo "[错误] basicsr 安装失败"; exit 1; fi

    echo "  [3/3] 验证..."
    python3 -c "import cv2, torch, numpy, realesrgan, torchvision, tqdm, basicsr.archs.rrdbnet_arch" 2>/dev/null && echo "  安装完成 ✓" || { echo "[错误] 验证失败，请尝试手动安装"; exit 1; }
}

echo ""
echo "双击 开始处理v2.command 启动"
