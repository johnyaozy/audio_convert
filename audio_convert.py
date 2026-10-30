#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频批量转换脚本
功能：调用FFmpeg，将指定文件夹中指定格式的音频文件转换为目标格式
用法：python audio_convert.py <输入文件夹> <源格式> <目标格式> [输出文件夹]
示例：python audio_convert.py ./audio wav mp3
          python audio_convert.py ./audio flac mp3 ./output -b 192k
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path


def check_ffmpeg() -> bool:
    """检查系统中是否安装了FFmpeg"""
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def convert_audio(
    input_dir: str,
    src_format: str,
    dst_format: str,
    output_dir: str = None,
    bitrate: str = None,
    sample_rate: int = None,
    recursive: bool = False,
    overwrite: bool = False,
) -> None:
    """
    批量转换音频文件

    Args:
        input_dir:   输入文件夹路径
        src_format:  源音频格式（如 wav, flac, aiff）
        dst_format:  目标音频格式（如 mp3, ogg, m4a）
        output_dir:  输出文件夹（默认为输入目录下的 converted_<目标格式>）
        bitrate:     音频码率（如 192k），仅对有损格式有效
        sample_rate: 采样率（如 44100）
        recursive:   是否递归遍历子文件夹
        overwrite:   是否覆盖已存在的输出文件
    """
    src_format = src_format.lower().lstrip(".")
    dst_format = dst_format.lower().lstrip(".")

    input_path = Path(input_dir).resolve()
    if not input_path.is_dir():
        print(f"❌ 错误：输入文件夹不存在 -> {input_path}")
        sys.exit(1)

    # 输出目录：默认放在输入目录下
    if output_dir is None:
        output_path = input_path / f"converted_{dst_format}"
    else:
        output_path = Path(output_dir).resolve()
    output_path.mkdir(parents=True, exist_ok=True)

    # 查找匹配的文件
    pattern = f"**/*.{src_format}" if recursive else f"*.{src_format}"
    files = sorted(input_path.glob(pattern))
    # 排除"输出目录中已存在同名目标格式文件"，避免二次运行时重复处理。
    # 注意：不再按"目录包含关系"排除——否则当输入目录 == 输出目录（原地转换）时，
    # 所有源文件的父目录都等于输出目录，会被全部误杀，导致报"未找到源文件"。
    def _expected_out(f: Path) -> Path:
        p = output_path / f"{f.stem}.{dst_format}"
        if recursive and f.parent != input_path:
            p = output_path / f.parent.relative_to(input_path) / f"{f.stem}.{dst_format}"
        return p

    files = [f for f in files if not _expected_out(f).exists()]

    if not files:
        print(f"⚠️  未找到 .{src_format} 格式的文件（目录: {input_path}）")
        sys.exit(0)

    print(f"🔍 共找到 {len(files)} 个 .{src_format} 文件，开始转换...\n")

    success, failed = [], []

    for i, file in enumerate(files, 1):
        out_file = output_path / f"{file.stem}.{dst_format}"

        # 相对路径保持子目录结构（递归模式）
        if recursive and file.parent != input_path:
            rel_parent = file.parent.relative_to(input_path)
            out_file = output_path / rel_parent / f"{file.stem}.{dst_format}"
            out_file.parent.mkdir(parents=True, exist_ok=True)

        if out_file.exists() and not overwrite:
            print(f"[{i}/{len(files)}] ⏭️  已存在，跳过 -> {out_file.name}")
            continue

        # 构建 FFmpeg 命令（-n 不覆盖 / -y 覆盖）
        cmd = ["ffmpeg", "-y" if overwrite else "-n", "-i", str(file)]
        if bitrate:
            cmd += ["-b:a", bitrate]
        if sample_rate:
            cmd += ["-ar", str(sample_rate)]
        cmd += [str(out_file)]

        print(f"[{i}/{len(files)}] 🔄 {file.name} -> {out_file.name}")

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            success.append(out_file)
        else:
            failed.append((file, result.stderr.decode(errors="ignore")))
            print(f"         ❌ 失败: {result.stderr.decode(errors='ignore').splitlines()[-1]}")

    # 汇总
    print("\n" + "=" * 50)
    print(f"✅ 成功: {len(success)} 个")
    if failed:
        print(f"❌ 失败: {len(failed)} 个，详情：")
        for f, err in failed:
            print(f"   - {f.name}")
    print(f"📁 输出目录: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="调用FFmpeg批量转换音频格式")
    parser.add_argument("input_dir", help="输入文件夹路径")
    parser.add_argument("src_format", help="源格式（如 wav）")
    parser.add_argument("dst_format", help="目标格式（如 mp3）")
    parser.add_argument("-o", "--output-dir", default=None, help="输出文件夹（默认为输入目录/converted_<格式>）")
    parser.add_argument("-b", "--bitrate", default=None, help="音频码率，如 192k（默认FFmpeg自动）")
    parser.add_argument("-sr", "--sample-rate", type=int, default=None, help="采样率，如 44100")
    parser.add_argument("-r", "--recursive", action="store_true", help="递归处理子文件夹")
    parser.add_argument("-y", "--overwrite", action="store_true", help="覆盖已存在的输出文件")
    args = parser.parse_args()

    if not check_ffmpeg():
        print("❌ 错误：未检测到 FFmpeg，请先安装并加入 PATH。")
        print("   安装方法：")
        print("   - Ubuntu/Debian: sudo apt install ffmpeg")
        print("   - macOS:         brew install ffmpeg")
        print("   - Windows:       https://ffmpeg.org/download.html 或 winget install ffmpeg")
        sys.exit(1)

    convert_audio(
        input_dir=args.input_dir,
        src_format=args.src_format,
        dst_format=args.dst_format,
        output_dir=args.output_dir,
        bitrate=args.bitrate,
        sample_rate=args.sample_rate,
        recursive=args.recursive,
        overwrite=args.overwrite,
    )


if __name__ == "__main__":
    main()
