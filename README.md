# 电商详情图切割 AI 高清化处理

用于监听输入目录中的详情图，按竖向白色间隙自动切列，并对每一列进行 4x AI 超分处理。

## 目录

- `mac/`：macOS 启动和处理脚本
- `windows/`：Windows 启动、安装和处理脚本
- `放入图片/`：拖入待处理图片
- `处理结果/`：输出切列和超分后的图片

## 使用

### macOS

1. 双击 `mac/setup.command` 安装依赖。
2. 双击 `mac/开始处理.command` 启动监听。
3. 把图片拖入 `mac/放入图片/`。
4. 在 `mac/处理结果/` 查看输出。

### Windows

1. 安装 Python 3.14。
2. 双击 `windows/setup.bat` 安装依赖。
3. 双击 `windows/开始处理.bat` 启动监听。
4. 把图片拖入 `windows/放入图片/`。
5. 在 `windows/处理结果/` 查看输出。

## 输入图片要求

当前切列逻辑基于固定业务前提：列与列之间存在贯穿全高的白色竖向间隙。若图片没有这种间隙，或内容里存在贯穿全高的白色竖线，可能导致无法识别或误切。

## 大文件说明

GitHub 普通仓库不适合直接提交大模型和离线 Python wheels。本仓库默认不包含：

- `mac/models/*.pth`
- `windows/models/*.pth`
- `windows/wheels/*`

本地运行或打包离线版时，需要把 `RealESRGAN_x4plus.pth` 放入对应的 `models/` 目录，并按平台准备依赖文件。
