# 🎬 视频下载器 Pro

一款支持多平台的视频下载工具，支持画质选择、字幕下载、AI字幕生成等功能。

## 快速开始（开发者）

### 开发模式运行

```bash
pip install -r requirements.txt
python video_downloader.py
```

### 打包为 exe（给用户使用）

```bash
# 1. 安装打包工具
pip install pyinstaller

# 2. 运行打包
python build.py

# 3. 生成的 exe 在 dist 文件夹中
```

### 打包后的文件结构

```
dist/
├── 视频下载器Pro.exe    # 主程序（单文件，双击运行）
├── bin/                 # FFmpeg（首次运行自动复制）
└── models/              # AI模型（首次运行自动下载）
```

## 用户使用指南

### 安装

1. 从开发者获取 `视频下载器Pro.exe`
2. 双击运行即可（无需安装 Python）

### 使用

1. 复制视频链接
2. 粘贴到输入框
3. 选择画质
4. 点击下载

### 常见问题

- **首次运行较慢**：需要下载 AI 模型（~75MB）
- **下载失败**：尝试切换画质或导入 Cookie

## 功能特性

| 功能 | 说明 |
|------|------|
| 🎯 多画质选择 | 4K / 1080P / 720P / 480P |
| 📝 字幕下载 | 自动下载并嵌入视频 |
| 🤖 AI字幕 | 使用 Whisper 生成字幕 |
| 🧼 去水印 | 自动去除视频水印 |
| ☁️ 多平台 | YouTube、B站、抖音等 |

## 快速开始

### Windows

```bash
# 方式1: 一键安装
python install.py

# 方式2: 手动运行
pip install -r requirements.txt
python video_downloader.py
```

### macOS

```bash
# 安装 FFmpeg
brew install ffmpeg

# 安装依赖
pip3 install -r requirements.txt

# 运行
python3 video_downloader.py
```

## 使用指南

### 1. 基本下载

1. 复制视频链接
2. 粘贴到输入框
3. 选择画质（默认最高）
4. 点击下载

### 2. 字幕下载

在"字幕下载"下拉菜单中选择：
- **不需要** - 不下载字幕
- **英文字幕** - 下载英文字幕
- **中文字幕** - 下载中文字幕
- **中英双语** - 下载双语字幕

> ⚠️ 注意：字幕将嵌入视频，默认不显示，需要用 VLC 等播放器手动开启

### 3. 抖音下载

抖音视频需要登录 Cookie：

1. 安装浏览器扩展 [Cookie-Editor](https://cookie-editor.cgagnier.ca/)
2. 登录抖音网页版
3. 点击扩展 → 导出为 Netscape 格式
4. 在"高级设置"中导入 Cookie 文件

### 4. AI 字幕

对于没有字幕的视频，可以使用 AI 自动生成：

1. 切换到"添加字幕"标签
2. 选择本地视频文件
3. 选择字幕语言
4. 点击"生成字幕"

> 🤖 AI 字幕使用 Whisper 模型，首次使用会下载模型（约75MB）

## 支持的平台

- ✅ YouTube
- ✅ 哔哩哔哩 (B站)
- ✅ 抖音
- ✅ 腾讯视频
- ✅ 爱奇艺
- ✅ 优酷
- ✅ 更多...

## 常见问题

### 下载失败怎么办？

1. **提示"不支持的网站"**
   - 检查链接是否正确
   - 抖音需要导入 Cookie

2. **提示"需要登录"**
   - 视频可能需要 VIP
   - 或需要导入 Cookie

3. **下载太慢**
   - 检查网络连接
   - 可以尝试切换画质

4. **4K 下载失败**
   - 确保网络稳定
   - 尝试使用 VPN

### 字幕不显示？

- 字幕已嵌入视频文件内部
- 需要用 VLC 播放器：右键 → 字幕 → 启用

## 项目结构

```
video-downloader/
├── video_downloader.py   # 主程序
├── requirements.txt       # Python 依赖
├── install.py            # 安装脚本
├── bin/                  # FFmpeg (Windows)
└── models/               # AI 模型
```

## 技术栈

- **GUI**: CustomTkinter
- **下载**: yt-dlp
- **AI 字幕**: Faster Whisper
- **视频处理**: FFmpeg

## 许可证

MIT License
