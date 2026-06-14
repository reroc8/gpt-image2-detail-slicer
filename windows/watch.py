"""
监听 放入图片\ 自动切割+超分 (Windows 版)
用法: python watch.py  (持续运行)
"""

import os
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import torch
from realesrgan import RealESRGANer
from basicsr.archs.rrdbnet_arch import RRDBNet

BASE   = Path(__file__).resolve().parent
INPUT  = BASE / "放入图片"
OUTPUT = BASE / "处理结果"
DONE   = INPUT / ".done"
MODEL  = BASE / "models" / "RealESRGAN_x4plus.pth"
SCALE  = 4
TILE   = 512
POLL   = 2

SUPP = {'.png', '.jpg', '.jpeg', '.webp', '.tiff', '.tif', '.bmp'}


def init_upsampler():
    if not MODEL.exists():
        print(f"\n[错误] {MODEL}")
        sys.exit(1)

    model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=SCALE)

    if torch.cuda.is_available():
        dev = torch.device("cuda")
        print(f"  CUDA: {torch.cuda.get_device_name(0)}")
    else:
        dev = torch.device("cpu")
        print("  CPU")

    return RealESRGANer(scale=SCALE, model_path=str(MODEL), model=model,
                        tile=TILE, tile_pad=10, pre_pad=0,
                        half=torch.cuda.is_available(), device=dev)


def split(img):
    h, w = img.shape[:2]
    cw = w // 4
    if cw < 1: return []
    cols = []
    for i in range(4):
        s = i * cw
        e = w if i == 3 else (i + 1) * cw
        cols.append(img[:, s:e])
    return cols


def upscale(up, img):
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    elif img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    out, _ = up.enhance(img, outscale=SCALE)
    return out


def handle(img_path: Path, up):
    stem = img_path.stem
    ext  = img_path.suffix
    # cv2.imread 在 Windows 上不支持中文路径，用 imdecode 代替
    raw = np.fromfile(str(img_path), dtype=np.uint8)
    img = cv2.imdecode(raw, cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"  X 无法读取")
        return False

    cols = split(img)
    if not cols:
        print(f"  X 宽度太小")
        return False

    sub = OUTPUT / stem
    sub.mkdir(parents=True, exist_ok=True)

    for i, c in enumerate(cols):
        t0 = time.time()
        r = upscale(up, c)
        dt = time.time() - t0
        p = sub / f"{stem}_c{i+1}_x{SCALE}{ext}"
        ok, buf = cv2.imencode(ext, r, [cv2.IMWRITE_PNG_COMPRESSION, 0])
        if ok:
            buf.tofile(str(p))
        print(f"    c{i+1}/4: {c.shape[1]}x{c.shape[0]} -> {r.shape[1]}x{r.shape[0]} ({dt:.1f}s)")

    DONE.mkdir(parents=True, exist_ok=True)
    img_path.rename(DONE / img_path.name)
    return True


def scan(up, seen: set):
    for f in sorted(INPUT.iterdir()):
        if not f.is_file(): continue
        if f.name.startswith('.'): continue
        if f.suffix.lower() not in SUPP: continue
        if f.name in seen: continue

        seen.add(f.name)
        print(f"\n[{time.strftime('%H:%M:%S')}] {f.name} ({f.stat().st_size//1024}KB)")
        try:
            handle(f, up)
            print(f"  v -> 处理结果\\{f.stem}\\")
        except Exception as e:
            print(f"  X 错误: {e}")


def main():
    INPUT.mkdir(parents=True, exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)

    print("=" * 46)
    print("  电商详情图切割AI高清化处理0.9")
    print("  内部使用 请勿外传")
    print("=" * 46)
    print(f"  放入: {INPUT}")
    print(f"  输出: {OUTPUT}")
    up = init_upsampler()
    print(f"\n  就绪，拖图到 放入图片\\ 自动处理\n")

    seen = set()
    try:
        while True:
            scan(up, seen)
            time.sleep(POLL)
    except KeyboardInterrupt:
        print("\n  已停止")


if __name__ == "__main__":
    main()
