#!/usr/bin/env python3
"""
视频下载器 - 跨平台一键安装脚本
支持: Windows, macOS, Linux
"""

import os
import sys
import subprocess
import platform

def get_system():
    return platform.system()  # 'Windows', 'Darwin', 'Linux'

def install_python_deps():
    """安装Python依赖"""
    print("📦 安装 Python 依赖...")
    
    deps = [
        "customtkinter>=5.2.0",
        "yt-dlp>=2024.12.0", 
        "faster-whisper>=0.10.0",
        "pillow>=10.0.0",
        "requests>=2.31.0"
    ]
    
    for dep in deps:
        result = subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  ❌ 安装失败: {dep}")
            print(f"     {result.stderr[:100]}")
        else:
            print(f"  ✅ {dep}")

def install_ffmpeg():
    """安装 ffmpeg"""
    system = get_system()
    print("🎬 安装 FFmpeg...")
    
    if system == "Windows":
        # Windows: 下载并解压
        ffmpeg_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin")
        if os.path.exists(ffmpeg_dir):
            print("  ✅ FFmpeg 已存在")
            return
        
        os.makedirs(ffmpeg_dir, exist_ok=True)
        
        # 下载 ffmpeg
        url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        zip_path = os.path.join(ffmpeg_dir, "ffmpeg.zip")
        
        print("  ⬇️ 下载 FFmpeg (约 90MB)...")
        try:
            import urllib.request
            urllib.request.urlretrieve(url, zip_path)
            
            # 解压
            print("  📦 解压中...")
            import zipfile
            with zipfile.ZipFile(zip_path, 'r') as z:
                for member in z.namelist():
                    if 'ffmpeg.exe' in member:
                        z.extract(member, ffmpeg_dir)
            
            # 移动到正确位置
            for root, dirs, files in os.walk(ffmpeg_dir):
                for f in files:
                    if f == 'ffmpeg.exe':
                        src = os.path.join(root, f)
                        dst = os.path.join(ffmpeg_dir, 'ffmpeg.exe')
                        if src != dst:
                            import shutil
                            shutil.move(src, dst)
            
            os.remove(zip_path)
            print("  ✅ FFmpeg 安装完成!")
            
        except Exception as e:
            print(f"  ❌ FFmpeg 安装失败: {e}")
            print("  请手动从 https://ffmpeg.org/download.html 下载")
            
    elif system == "Darwin":
        # macOS: 使用 brew
        result = subprocess.run(["brew", "install", "ffmpeg"], capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✅ FFmpeg 安装完成!")
        else:
            print("  ❌ 请运行: brew install ffmpeg")
            
    else:
        # Linux: 使用 apt
        result = subprocess.run(["sudo", "apt", "install", "-y", "ffmpeg"], capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✅ FFmpeg 安装完成!")
        else:
            print("  ❌ 请运行: sudo apt install ffmpeg")

def create_launcher():
    """创建启动脚本"""
    system = get_system()
    
    if system == "Windows":
        script = """@echo off
cd /d "%~dp0"
python video_downloader.py
pause
"""
        with open("启动下载器.bat", "w", encoding="utf-8") as f:
            f.write(script)
        print("  ✅ 已创建: 启动下载器.bat")
        
    else:
        script = """#!/bin/bash
cd "$(dirname "$0")"
python3 video_downloader.py
"""
        with open("启动下载器.command", "w") as f:
            f.write(script)
        os.chmod("启动下载器.command", 0o755)
        print("  ✅ 已创建: 启动下载器.command")

def main():
    print("=" * 50)
    print("🎬 视频下载器 - 一键安装")
    print(f"   系统: {platform.system()} {platform.release()}")
    print("=" * 50)
    print()
    
    # 安装 Python 依赖
    install_python_deps()
    print()
    
    # 安装 FFmpeg
    install_ffmpeg()
    print()
    
    # 创建启动脚本
    create_launcher()
    
    print()
    print("=" * 50)
    print("✅ 安装完成!")
    print()
    print("启动方式:")
    print("  Windows: 双击 启动下载器.bat")
    print("  Mac: 双击 启动下载器.command")
    print("  或运行: python video_downloader.py")
    print("=" * 50)

if __name__ == "__main__":
    main()
