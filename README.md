# GPT Image 2 详情图切列高清器

GitHub 仓库名：`gpt-image2-detail-slicer`

用于切割并高清化由 GPT Image 2 生成的电商详情图。

本工具会监听输入目录中的详情图，按竖向白色间隙自动切列，并对每一列进行 4x AI 超分处理。

## 适用场景

本项目主要面向 GPT Image 2 生成的电商详情图。默认这类图片按多列排版，并使用贯穿全高的白色竖向间隙分隔各列。

因此，项目采用简单稳定的白色竖向间隙检测方式来切列，而不是通用图片版面识别算法。

早期版本曾使用固定四等分切割；当前版本已统一为基于白色竖向间隙的自适应切列，项目中只保留这一套正式处理逻辑。

## 目录

- `mac/`：macOS 启动和处理脚本
- `windows/`：Windows 启动、安装和处理脚本
- `放入图片/`：拖入待处理图片
- `处理结果/`：输出切列和超分后的图片

## Release 下载建议

GitHub Release 建议按平台下载，不需要下载源码压缩包。

- `GPT-Image2-Detail-Slicer-v0.9.0-mac.zip`：macOS 包，内置模型，安装依赖时需要联网。
- `GPT-Image2-Detail-Slicer-v0.9.0-windows-online.zip`：Windows 小包，内置模型，安装依赖时需要联网。
- `GPT-Image2-Detail-Slicer-v0.9.0-windows-offline-full.zip`：Windows 离线完整包，内置模型和离线依赖，文件较大。

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

图片需符合以下业务前提：

- 图片来源主要为 GPT Image 2 生成的电商详情图。
- 列与列之间存在贯穿全高的白色竖向间隙。
- 内容区域不要出现贯穿全高的白色竖线，否则可能被误判为分隔线。

如果输入图片不符合以上格式，可能导致无法识别列数或切割位置不准确。

## 大文件说明

GitHub 普通仓库不适合直接提交大模型和离线 Python wheels。完整可运行包放在 GitHub Release 中，源码仓库默认不包含：

- `mac/models/*.pth`
- `windows/models/*.pth`
- `windows/wheels/*`

如果只下载源码，需要把 `RealESRGAN_x4plus.pth` 放入对应的 `models/` 目录。Windows 离线版还需要准备 `windows/wheels/` 依赖文件；Windows 在线版可由 `setup.bat` 联网安装依赖。
