"""
GPT Image 2 详情图切列高清器 0.9 - 自适应列检测
自动识别列数，精准切在间隙处，去白边
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
SUPP   = {'.png', '.jpg', '.jpeg', '.webp', '.tiff', '.tif', '.bmp'}


def init_upsampler():
    if not MODEL.exists():
        print(f"\n[错误] {MODEL}")
        sys.exit(1)
    mdl = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=SCALE)
    if torch.cuda.is_available():
        print(f"  CUDA: {torch.cuda.get_device_name(0)}")
    else:
        print("  CPU")
    return RealESRGANer(scale=SCALE, model_path=str(MODEL), model=mdl,
                        tile=TILE, tile_pad=10, pre_pad=0,
                        half=torch.cuda.is_available())


def detect_columns(img):
    """贯穿全高的白色竖列 = 列间隙（容许少量深色像素）"""
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 每列白色像素占比 ≥ 99% → 视为间隙列（1000px 高允许 10px 非白）
    WHITE = 235
    white_ratio = (gray > WHITE).sum(axis=0) / h  # (w,)
    is_white_col = white_ratio >= 0.99

    # 合并相邻白色列为间隙区间
    gaps = []
    in_gap = False
    gap_start = 0
    for x in range(w):
        if is_white_col[x] and not in_gap:
            gap_start = x
            in_gap = True
        elif not is_white_col[x] and in_gap:
            gaps.append((gap_start, x))
            in_gap = False
    if in_gap:
        gaps.append((gap_start, w))

    # 去掉左右边缘的空白（页面边距）
    inner = [(s, e) for s, e in gaps if s > 0 and e < w]
    if not inner:
        return []

    # 列 = 间隙之间的区间
    cols = []
    prev = 0
    for s, e in inner:
        if s - prev > 0:
            cols.append((prev, s))
        prev = e
    if w - prev > 0:
        cols.append((prev, w))

    return cols


def trim_white(img, margin=3):
    """去除白边（保守，避免误裁内容），兼容 RGBA"""
    # 取 RGB 通道计算灰度
    src = img[..., :3] if img.ndim == 3 and img.shape[2] >= 3 else img
    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY) if src.ndim == 3 else src
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

    coords = cv2.findNonZero(thresh)
    if coords is None:
        return img

    x, y, w, h = cv2.boundingRect(coords)
    x1 = max(0, x - margin)
    y1 = max(0, y - margin)
    x2 = min(img.shape[1], x + w + margin)
    y2 = min(img.shape[0], y + h + margin)

    return img[y1:y2, x1:x2]


def upscale(up, img):
    """超分，保留 alpha 通道"""
    has_alpha = img.ndim == 3 and img.shape[2] == 4
    if has_alpha:
        alpha = img[:, :, 3]
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    elif img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    out, _ = up.enhance(img, outscale=SCALE)

    if has_alpha:
        alpha_up = cv2.resize(alpha, (out.shape[1], out.shape[0]),
                              interpolation=cv2.INTER_LANCZOS4)
        out = cv2.cvtColor(out, cv2.COLOR_BGR2BGRA)
        out[:, :, 3] = alpha_up
    return out


def handle(img_path: Path, up):
    stem = img_path.stem
    ext  = img_path.suffix

    raw = np.fromfile(str(img_path), dtype=np.uint8)
    img = cv2.imdecode(raw, cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"  X 无法读取")
        return False

    # 保留原图用于检测（列检测用 BGR），超分保留 alpha
    has_alpha = img.ndim == 3 and img.shape[2] == 4
    img_bgr = img.copy()
    if has_alpha:
        img_bgr = cv2.cvtColor(img_bgr, cv2.COLOR_BGRA2BGR)
    elif img.ndim == 2:
        img_bgr = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    # 自适应检测列
    cols = detect_columns(img_bgr)
    n = len(cols)
    if n == 0:
        print(f"  X 未检测到列")
        return False

    print(f"  检测到 {n} 列")

    ts = int(time.time())
    sub = OUTPUT / f"{stem}_{ts}"
    while sub.exists():
        ts += 1
        sub = OUTPUT / f"{stem}_{ts}"
    sub.mkdir(parents=True, exist_ok=True)

    ok_all = True
    for i, (x1, x2) in enumerate(cols):
        col = img[:, x1:x2]  # 保留 alpha 的原图切片
        o_h, o_w = col.shape[:2]

        # 去白边
        col = trim_white(col)

        t0 = time.time()
        r = upscale(up, col)
        dt = time.time() - t0

        p = sub / f"{stem}_c{i+1}_x{SCALE}{ext}"
        ok, buf = cv2.imencode(ext, r, [cv2.IMWRITE_PNG_COMPRESSION, 0])
        if ok:
            buf.tofile(str(p))
        else:
            print(f"    c{i+1}/{n}: 写入失败")
            ok_all = False
            continue
        print(f"    c{i+1}/{n}: {o_w}x{o_h} -> {r.shape[1]}x{r.shape[0]} ({dt:.1f}s)")

    if ok_all:
        DONE.mkdir(parents=True, exist_ok=True)
        dest = DONE / img_path.name
        if dest.exists():
            dest = DONE / f"{img_path.stem}_{int(time.time())}{img_path.suffix}"
        img_path.rename(dest)

    return ok_all


def scan(up, seen: set):
    for f in sorted(INPUT.iterdir()):
        if not f.is_file(): continue
        if f.name.startswith('.'): continue
        if f.suffix.lower() not in SUPP: continue
        key = (f.name, f.stat().st_size, f.stat().st_mtime_ns)
        if key in seen: continue
        print(f"\n[{time.strftime('%H:%M:%S')}] {f.name} ({f.stat().st_size//1024}KB)")
        try:
            ok = handle(f, up)
            if ok:
                seen.add(key)
                print(f"  v -> 处理结果\\{f.stem}\\")
        except Exception as e:
            print(f"  X 错误: {e}")


def main():
    INPUT.mkdir(parents=True, exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)

    print("=" * 50)
    print("  GPT Image 2 详情图切列高清器 0.9")
    print("  自适应列检测 · 去白边 · 4x超分")
    print("  内部使用 请勿外传")
    print("=" * 50)
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
