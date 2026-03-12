# 视频下载器 Pro - 一键打包脚本

# 使用方法:
# 1. 安装打包工具: pip install pyinstaller
# 2. 运行打包: python build.py
# 3. 生成的 exe 在 dist 文件夹中

import os
import sys
import subprocess

def install_deps():
    """安装所需依赖"""
    print("安装依赖...")
    deps = [
        "pyinstaller>=6.0",
        "customtkinter>=5.2.0",
        "yt-dlp>=2024.12.0",
        "faster-whisper>=0.10.0",
        "pillow>=10.0.0",
        "requests>=2.31.0"
    ]
    for dep in deps:
        subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
    print("依赖安装完成!")

def build_exe():
    """打包为exe"""
    print("开始打包...")
    
    # PyInstaller 命令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=视频下载器Pro",
        "--windowed",  # 不显示控制台
        "--onefile",   # 打包为单个文件
        "--icon=icon.ico",  # 图标（可选）
        "--add-data=bin;bin",  # 包含FFmpeg
        "--add-data=models;models",  # 包含Whisper模型
        "--hidden-import=ctypes",
        "--hidden-import=tkinter",
        "--hidden-import=customtkinter",
        "--hidden-import=PIL",
        "--hidden-import=yt_dlp",
        "--hidden-import=faster_whisper",
        "--collect-all=customtkinter",
        "--collect-all=faster_whisper",
        "--noconfirm",  # 覆盖已存在的文件
        "video_downloader.py"
    ]
    
    # 如果没有图标，去掉icon参数
    if not os.path.exists("icon.ico"):
        cmd.remove("--icon=icon.ico")
    
    subprocess.run(cmd)
    print("打包完成!")
    print("exe文件在 dist 文件夹中")

def main():
    print("="*50)
    print("视频下载器 Pro - 打包工具")
    print("="*50)
    
    # 检查是否安装了pyinstaller
    try:
        subprocess.run([sys.executable, "-m", "pyinstaller", "--version"], 
                      capture_output=True, check=True)
    except:
        print("未安装 PyInstaller，正在安装...")
        install_deps()
    
    # 开始打包
    build_exe()
    
    print("\n" + "="*50)
    print("打包完成!")
    print("运行: python build.py")
    print("="*50)

if __name__ == "__main__":
    main()
