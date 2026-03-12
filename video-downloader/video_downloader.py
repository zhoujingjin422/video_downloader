#!/usr/bin/env python3
"""
视频下载器 Pro - 支持画质选择和字幕添加
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import yt_dlp
import threading
import os
import re
import subprocess
import shutil
import time
from datetime import datetime
from tkinter import ttk

# ========== 主题配置 ==========
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# 配色方案
COLORS = {
    "bg_main": "#0F0F1A",
    "bg_card": "#1A1A2E",
    "bg_input": "#252542",
    "primary": "#00D4FF",
    "primary_hover": "#00B8D4",
    "success": "#00C853",
    "warning": "#FF9100",
    "error": "#FF5252",
    "text_main": "#FFFFFF",
    "text_secondary": "#B0B0C0",
    "border": "#3A3A5A",
}


class VideoDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("视频下载器 Pro")
        self.geometry("780x720")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_main"])
        
        # 数据
        self.download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        self.cookie_file = ""
        self.current_task = None
        self.download_history = []
        self.last_error = ""
        self.available_formats = []  # 可用画质
        
        # 字体
        self.font_title = ctk.CTkFont("微软雅黑", 22, "bold")
        self.font_normal = ctk.CTkFont("微软雅黑", 12)
        self.font_small = ctk.CTkFont("微软雅黑", 10)
        
        # 加载历史记录
        self.load_history()
        
        self.create_widgets()
        
    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        
        # ========== 顶部标题栏 ==========
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="ew")
        
        self.title_label = ctk.CTkLabel(
            self.header, 
            text="🎬 视频下载器 Pro",
            font=self.font_title,
            text_color=COLORS["primary"]
        )
        self.title_label.pack(side="left")
        
        # 功能切换标签
        self.tab_var = ctk.StringVar(value="download")
        self.tab_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        self.tab_frame.pack(side="left", padx=30)
        
        self.download_tab = ctk.CTkRadioButton(
            self.tab_frame,
            text="📥 下载",
            variable=self.tab_var,
            value="download",
            command=self.switch_tab,
            font=self.font_normal
        )
        self.download_tab.pack(side="left", padx=10)
        
        self.subtitle_tab = ctk.CTkRadioButton(
            self.tab_frame,
            text="📝 添加字幕",
            variable=self.tab_var,
            value="subtitle",
            command=self.switch_tab,
            font=self.font_normal
        )
        self.subtitle_tab.pack(side="left", padx=10)
        
        # 设置按钮
        self.settings_btn = ctk.CTkButton(
            self.header,
            text="⚙️",
            width=40,
            fg_color="transparent",
            border_width=1,
            border_color=COLORS["border"],
            command=self.toggle_settings
        )
        self.settings_btn.pack(side="right")
        
        # ========== 下载功能区 ==========
        self.download_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.download_frame.grid(row=1, column=0, padx=0, pady=0, sticky="nsew")
        self.download_frame.grid_columnconfigure(0, weight=1)
        
        # 主输入卡片
        self.input_card = ctk.CTkFrame(self.download_frame, fg_color=COLORS["bg_card"], corner_radius=15)
        self.input_card.grid(row=0, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.input_card.grid_columnconfigure(0, weight=1)
        
        # 链接输入
        self.url_label = ctk.CTkLabel(
            self.input_card, 
            text="📎 视频链接",
            font=self.font_normal,
            text_color=COLORS["text_secondary"]
        )
        self.url_label.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")
        
        self.url_entry = ctk.CTkEntry(
            self.input_card,
            placeholder_text="粘贴视频链接 (腾讯/B站/YouTube/抖音...)",
            height=45,
            font=self.font_normal,
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            placeholder_text_color=COLORS["text_secondary"]
        )
        self.url_entry.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        
        # 画质选择
        self.quality_frame = ctk.CTkFrame(self.input_card, fg_color="transparent")
        self.quality_frame.grid(row=2, column=0, padx=20, pady=(10, 5), sticky="ew")
        self.quality_frame.grid_columnconfigure(1, weight=1)
        
        self.quality_label = ctk.CTkLabel(
            self.quality_frame,
            text="🎯 画质选择",
            font=self.font_normal,
            text_color=COLORS["text_secondary"]
        )
        self.quality_label.grid(row=0, column=0, sticky="w")
        
        self.quality_var = ctk.StringVar(value="最高")
        self.quality_combo = ctk.CTkOptionMenu(
            self.quality_frame,
            values=["最高", "4K", "1080P", "720P", "480P"],
            variable=self.quality_var,
            fg_color=COLORS["bg_input"],
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"],
            width=120
        )
        self.quality_combo.grid(row=0, column=1, sticky="w", padx=10)
        
        self.quality_tip = ctk.CTkLabel(
            self.quality_frame,
            text="(默认最高画质)",
            font=self.font_small,
            text_color=COLORS["text_secondary"]
        )
        self.quality_tip.grid(row=0, column=2, sticky="w")
        
        # 字幕下载选项
        self.subtitle_select_frame = ctk.CTkFrame(self.input_card, fg_color="transparent")
        self.subtitle_select_frame.grid(row=3, column=0, padx=20, pady=(10, 5), sticky="ew")
        self.subtitle_select_frame.grid_columnconfigure(1, weight=1)
        
        self.subtitle_select_label = ctk.CTkLabel(
            self.subtitle_select_frame,
            text="📝 字幕下载",
            font=self.font_normal,
            text_color=COLORS["text_secondary"]
        )
        self.subtitle_select_label.grid(row=0, column=0, sticky="w")
        
        self.subtitle_select_var = ctk.StringVar(value="无")
        self.subtitle_select_combo = ctk.CTkOptionMenu(
            self.subtitle_select_frame,
            values=["无", "英文字幕", "中文字幕", "中英双语"],
            variable=self.subtitle_select_var,
            fg_color=COLORS["bg_input"],
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"],
            width=120
        )
        self.subtitle_select_combo.grid(row=0, column=1, sticky="w", padx=10)
        
        self.subtitle_select_tip = ctk.CTkLabel(
            self.subtitle_select_frame,
            text="(下载字幕并嵌入视频)",
            font=self.font_small,
            text_color=COLORS["text_secondary"]
        )
        self.subtitle_select_tip.grid(row=0, column=2, sticky="w")
        
        # 文件名和路径
        self.name_label = ctk.CTkLabel(
            self.input_card, 
            text="💾 保存名称",
            font=self.font_normal,
            text_color=COLORS["text_secondary"]
        )
        self.name_label.grid(row=3, column=0, padx=20, pady=(10, 5), sticky="w")
        
        self.name_entry = ctk.CTkEntry(
            self.input_card,
            placeholder_text="留空则使用原视频标题",
            height=40,
            font=self.font_normal,
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"]
        )
        self.name_entry.grid(row=4, column=0, padx=20, pady=5, sticky="ew")
        
        # 保存路径
        self.path_frame = ctk.CTkFrame(self.input_card, fg_color="transparent")
        self.path_frame.grid(row=5, column=0, padx=20, pady=(10, 10), sticky="ew")
        self.path_frame.grid_columnconfigure(0, weight=1)
        
        self.path_label = ctk.CTkLabel(
            self.path_frame, 
            text="📁 保存位置",
            font=self.font_normal,
            text_color=COLORS["text_secondary"]
        )
        self.path_label.grid(row=0, column=0, sticky="w")
        
        self.path_entry = ctk.CTkEntry(
            self.path_frame,
            height=38,
            font=self.font_normal,
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"]
        )
        self.path_entry.insert(0, self.download_dir)
        self.path_entry.grid(row=1, column=0, padx=(0, 10), sticky="ew")
        
        self.browse_btn = ctk.CTkButton(
            self.path_frame,
            text="📂",
            width=45,
            height=38,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=self.browse_folder
        )
        self.browse_btn.grid(row=1, column=1)
        
        # 高级选项 (可折叠)
        self.advanced_frame = ctk.CTkFrame(self.download_frame, fg_color=COLORS["bg_card"], corner_radius=15)
        self.advanced_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.advanced_frame.grid_columnconfigure(1, weight=1)
        self.advanced_frame.grid_remove()
        
        # Cookie
        self.cookie_label = ctk.CTkLabel(
            self.advanced_frame, 
            text="🍪 Cookie (VIP视频)",
            font=self.font_normal,
            text_color=COLORS["text_secondary"]
        )
        self.cookie_label.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")
        
        self.cookie_entry = ctk.CTkEntry(
            self.advanced_frame,
            placeholder_text="不登录则留空",
            height=38,
            font=self.font_small,
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"]
        )
        self.cookie_entry.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        
        self.cookie_btn = ctk.CTkButton(
            self.advanced_frame,
            text="选择",
            width=60,
            height=38,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=self.select_cookie
        )
        self.cookie_btn.grid(row=1, column=1, padx=(10, 20))
        
        self.cookie_help = ctk.CTkLabel(
            self.advanced_frame,
            text="💡 安装Cookie-Editor扩展 → 登录 → 导出",
            font=self.font_small,
            text_color=COLORS["text_secondary"]
        )
        self.cookie_help.grid(row=2, column=0, columnspan=2, padx=20, pady=(5, 10), sticky="w")
        
        # 去水印
        self.watermark_var = ctk.BooleanVar(value=False)
        self.watermark_check = ctk.CTkCheckBox(
            self.advanced_frame,
            text="🧼 下载后去除水印",
            variable=self.watermark_var,
            font=self.font_normal,
            text_color=COLORS["text_main"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"]
        )
        self.watermark_check.grid(row=3, column=0, columnspan=2, padx=20, pady=(10, 15), sticky="w")
        
        # 下载按钮
        self.download_btn = ctk.CTkButton(
            self.download_frame,
            text="⬇️ 开始下载",
            height=55,
            font=ctk.CTkFont("微软雅黑", 16, "bold"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            corner_radius=12,
            command=self.start_download
        )
        self.download_frame.rowconfigure(2, weight=0)
        self.download_btn.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        # 进度卡片
        self.progress_card = ctk.CTkFrame(self.download_frame, fg_color=COLORS["bg_card"], corner_radius=15)
        self.progress_card.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.progress_card.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(
            self.progress_card,
            text="等待下载...",
            font=self.font_normal,
            text_color=COLORS["text_secondary"]
        )
        self.status_label.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")
        
        self.progress_bar = ctk.CTkProgressBar(
            self.progress_card,
            height=8,
            corner_radius=4,
            progress_color=COLORS["primary"]
        )
        self.progress_bar.set(0)
        self.progress_bar.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        
        self.detail_frame = ctk.CTkFrame(self.progress_card, fg_color="transparent")
        self.detail_frame.grid(row=2, column=0, padx=20, pady=(5, 15), sticky="ew")
        self.detail_frame.grid_columnconfigure((0,1,2), weight=1)
        
        self.size_label = ctk.CTkLabel(self.detail_frame, text="大小: --", font=self.font_small, text_color=COLORS["text_secondary"])
        self.size_label.grid(row=0, column=0, sticky="w")
        self.speed_label = ctk.CTkLabel(self.detail_frame, text="速度: --", font=self.font_small, text_color=COLORS["text_secondary"])
        self.speed_label.grid(row=0, column=1, sticky="n")
        self.eta_label = ctk.CTkLabel(self.detail_frame, text="剩余: --", font=self.font_small, text_color=COLORS["text_secondary"])
        self.eta_label.grid(row=0, column=2, sticky="e")
        
        # 历史
        self.history_card = ctk.CTkFrame(self.download_frame, fg_color=COLORS["bg_card"], corner_radius=15)
        self.history_card.grid(row=4, column=0, padx=20, pady=(0, 15), sticky="ew")
        
        self.history_title = ctk.CTkLabel(
            self.history_card,
            text="📜 下载历史",
            font=self.font_normal,
            text_color=COLORS["text_secondary"]
        )
        self.history_title.grid(row=0, column=0, padx=20, pady=(12, 8), sticky="w")
        
        self.history_list = ctk.CTkLabel(
            self.history_card,
            text="暂无下载记录",
            font=self.font_small,
            text_color=COLORS["text_secondary"]
        )
        self.history_list.grid(row=1, column=0, padx=20, pady=(0, 12), sticky="w")
        
        # ========== 字幕功能区 ==========
        self.subtitle_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.subtitle_frame.grid(row=1, column=0, padx=0, pady=0, sticky="nsew")
        self.subtitle_frame.grid_columnconfigure(0, weight=1)
        self.subtitle_frame.grid_remove()
        
        self.sub_card = ctk.CTkFrame(self.subtitle_frame, fg_color=COLORS["bg_card"], corner_radius=15)
        self.sub_card.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        self.sub_card.grid_columnconfigure(0, weight=1)
        
        self.sub_title = ctk.CTkLabel(
            self.sub_card,
            text="📝 添加字幕到本地视频",
            font=self.font_title,
            text_color=COLORS["primary"]
        )
        self.sub_title.grid(row=0, column=0, padx=20, pady=(20, 15))
        
        # 视频选择
        self.video_label = ctk.CTkLabel(
            self.sub_card,
            text="🎬 选择视频",
            font=self.font_normal,
            text_color=COLORS["text_secondary"]
        )
        self.video_label.grid(row=1, column=0, padx=20, pady=(15, 5), sticky="w")
        
        self.video_entry = ctk.CTkEntry(
            self.sub_card,
            placeholder_text="点击选择视频文件",
            height=45,
            font=self.font_normal,
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"]
        )
        self.video_entry.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        
        self.video_btn = ctk.CTkButton(
            self.sub_card,
            text="📂",
            width=50,
            fg_color=COLORS["primary"],
            command=self.select_video
        )
        self.video_btn.grid(row=2, column=1, padx=(0, 20))
        
        # 字幕选择
        self.subtype_label = ctk.CTkLabel(
            self.sub_card,
            text="📋 字幕类型",
            font=self.font_normal,
            text_color=COLORS["text_secondary"]
        )
        self.subtype_label.grid(row=3, column=0, padx=20, pady=(15, 5), sticky="w")
        
        self.subtype_var = ctk.StringVar(value="中英")
        self.subtype_combo = ctk.CTkOptionMenu(
            self.sub_card,
            values=["中文字幕", "英文字幕", "中英双语"],
            variable=self.subtype_var,
            fg_color=COLORS["bg_input"],
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"],
            width=200
        )
        self.subtype_combo.grid(row=4, column=0, padx=20, pady=5, sticky="w")
        
        # 字幕来源
        self.subfile_label = ctk.CTkLabel(
            self.sub_card,
            text="📄 字幕文件 (可选)",
            font=self.font_normal,
            text_color=COLORS["text_secondary"]
        )
        self.subfile_label.grid(row=5, column=0, padx=20, pady=(15, 5), sticky="w")
        
        self.subfile_entry = ctk.CTkEntry(
            self.sub_card,
            placeholder_text="留空则尝试自动下载字幕",
            height=40,
            font=self.font_normal,
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"]
        )
        self.subfile_entry.grid(row=6, column=0, padx=20, pady=5, sticky="ew")
        
        self.subfile_btn = ctk.CTkButton(
            self.sub_card,
            text="📂",
            width=50,
            fg_color=COLORS["primary"],
            command=self.select_subtitle
        )
        self.subfile_btn.grid(row=6, column=1, padx=(0, 20))
        
        # 字幕说明
        self.sub_help = ctk.CTkLabel(
            self.sub_card,
            text="💡 支持SRT/ASS/SSA/VTT格式。留空则使用AI (Whisper)自动生成字幕！",
            font=self.font_small,
            text_color=COLORS["text_secondary"]
        )
        self.sub_help.grid(row=7, column=0, columnspan=2, padx=20, pady=(10, 0), sticky="w")
        
        # 添加字幕按钮
        self.add_sub_btn = ctk.CTkButton(
            self.sub_card,
            text="➕ 添加字幕",
            height=50,
            font=ctk.CTkFont("微软雅黑", 15, "bold"),
            fg_color=COLORS["success"],
            hover_color="#00A843",
            corner_radius=12,
            command=self.add_subtitle
        )
        self.add_sub_btn.grid(row=8, column=0, columnspan=2, padx=20, pady=(20, 20), sticky="ew")
        
        # 字幕状态
        self.sub_status = ctk.CTkLabel(
            self.sub_card,
            text="",
            font=self.font_normal,
            text_color=COLORS["text_secondary"]
        )
        self.sub_status.grid(row=9, column=0, columnspan=2, padx=20, pady=(0, 15))
        
    def switch_tab(self):
        tab = self.tab_var.get()
        if tab == "download":
            self.download_frame.grid()
            self.subtitle_frame.grid_remove()
            self.geometry("780x720")
        else:
            self.download_frame.grid_remove()
            self.subtitle_frame.grid()
            self.geometry("650x580")
    
    def toggle_settings(self):
        if self.advanced_frame.winfo_viewable():
            self.advanced_frame.grid_remove()
        else:
            self.advanced_frame.grid()
            self.geometry("780x780")
    
    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.download_dir)
        if folder:
            self.download_dir = folder
            self.path_entry.delete(0, ctk.END)
            self.path_entry.insert(0, folder)
    
    def select_cookie(self):
        file_path = filedialog.askopenfilename(
            title="选择Cookie文件",
            filetypes=[("All Files", "*.*"), ("JSON", "*.json"), ("Netscape", "*.txt")]
        )
        if file_path:
            self.cookie_file = file_path
            self.cookie_entry.delete(0, ctk.END)
            self.cookie_entry.insert(0, os.path.basename(file_path))
    
    def select_video(self):
        file_path = filedialog.askopenfilename(
            title="选择视频文件",
            filetypes=[("Video", "*.mp4 *.mkv *.avi *.mov *.webm"), ("All Files", "*.*")]
        )
        if file_path:
            self.video_entry.delete(0, ctk.END)
            self.video_entry.insert(0, file_path)
    
    def select_subtitle(self):
        file_path = filedialog.askopenfilename(
            title="选择字幕文件",
            filetypes=[("Subtitle", "*.srt *.ass *.ssa *.vtt"), ("All Files", "*.*")]
        )
        if file_path:
            self.subfile_entry.delete(0, ctk.END)
            self.subfile_entry.insert(0, file_path)
    
    def add_subtitle(self):
        video_path = self.video_entry.get().strip()
        if not video_path or not os.path.exists(video_path):
            self.sub_status.configure(text="❌ 请选择有效的视频文件", text_color=COLORS["error"])
            return
        
        sub_type = self.subtype_var.get()
        sub_file = self.subfile_entry.get().strip()
        
        self.add_sub_btn.configure(state="disabled", text="处理中...")
        
        thread = threading.Thread(target=self.do_add_subtitle, args=(video_path, sub_file, sub_type))
        thread.daemon = True
        thread.start()
    
    def do_add_subtitle(self, video_path, sub_file, sub_type):
        try:
            ffmpeg_path = self.get_ffmpeg_path()
            if not ffmpeg_path:
                self.sub_status.configure(text="❌ 未安装ffmpeg", text_color=COLORS["error"])
                self.add_sub_btn.configure(state="normal", text="➕ 添加字幕")
                return
            
            # 如果没有指定字幕文件，使用Whisper自动生成
            if not sub_file or not os.path.exists(sub_file):
                self.sub_status.configure(text="🎤 尝试AI生成字幕...", text_color=COLORS["warning"])
                
                # 根据选择的字幕类型确定语言
                if sub_type == "中文字幕" or sub_type == "中英双语":
                    lang = "zh"
                else:
                    lang = "en"
                
                # 使用Whisper生成字幕
                sub_file = self.generate_subtitle_whisper(video_path, lang)
                
                if not sub_file:
                    self.sub_status.configure(text="❌ AI生成字幕失败，请手动选择字幕文件", text_color=COLORS["error"])
                    self.add_sub_btn.configure(state="normal", text="➕ 添加字幕")
                    return
                else:
                    self.sub_status.configure(text=f"✅ AI生成字幕成功!", text_color=COLORS["success"])
            
            # 输出文件
            name, ext = os.path.splitext(video_path)
            output_path = f"{name}_字幕{ext}"
            
            # 构建ffmpeg命令
            if sub_type == "中文字幕":
                # 内嵌中文字幕
                cmd = [ffmpeg_path, '-i', video_path, '-vf', f"subtitles='{sub_file}'", '-c:a', 'copy', '-y', output_path]
            elif sub_type == "英文字幕":
                cmd = [ffmpeg_path, '-i', video_path, '-vf', f"subtitles='{sub_file}'", '-c:a', 'copy', '-y', output_path]
            else:  # 中英双语 - 使用特殊处理
                cmd = [ffmpeg_path, '-i', video_path, '-vf', f"subtitles='{sub_file}'", '-c:a', 'copy', '-y', output_path]
            
            self.sub_status.configure(text="⏳ 正在处理...", text_color=COLORS["warning"])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0 and os.path.exists(output_path):
                self.sub_status.configure(text=f"✅ 成功! 保存为: {os.path.basename(output_path)}", text_color=COLORS["success"])
            else:
                error_msg = result.stderr[-200:] if result.stderr else "未知错误"
                self.sub_status.configure(text=f"❌ 失败: {error_msg[:50]}", text_color=COLORS["error"])
                
        except Exception as e:
            self.sub_status.configure(text=f"❌ 错误: {str(e)[:30]}", text_color=COLORS["error"])
        finally:
            self.add_sub_btn.configure(state="normal", text="➕ 添加字幕")
    
    def download_subtitle(self, video_path):
        """尝试下载字幕"""
        # 本地视频无法下载字幕，返回None让Whisper生成
        return None
    
    def generate_subtitle_whisper(self, video_path, language="zh"):
        """使用Whisper自动生成字幕"""
        try:
            try:
                from faster_whisper import WhisperModel
            except ImportError:
                self.sub_status.configure(text="❌ 未安装faster-whisper，请运行: pip install faster-whisper", text_color=COLORS["error"])
                return None
            
            self.sub_status.configure(text="🔄 加载Whisper模型(首次较慢)...", text_color=COLORS["warning"])
            
            # 使用tiny模型 (最快，占用内存少)
            model_size = "tiny"
            
            try:
                # 下载模型并加载 (可能需要网络，超时时间设置为120秒)
                model = WhisperModel(model_size, device="cpu", compute_type="int8", local_files_only=False, download_root="./models")
            except Exception as model_err:
                error_str = str(model_err).lower()
                if "timeout" in error_str or "connection" in error_str:
                    self.sub_status.configure(text="❌ 网络超时，请检查网络连接", text_color=COLORS["error"])
                else:
                    self.sub_status.configure(text="❌ 模型加载失败，请手动选择字幕", text_color=COLORS["error"])
                return None
            
            self.sub_status.configure(text="🎤 正在识别语音...", text_color=COLORS["warning"])
            
            try:
                # 提取音频并转录
                segments, info = model.transcribe(
                    video_path, 
                    language=language,
                    beam_size=5,
                    vad_filter=True
                )
            except Exception as transcribe_err:
                print(f"转录错误: {transcribe_err}")
                self.sub_status.configure(text="❌ 语音识别失败，可能是视频无音轨", text_color=COLORS["error"])
                return None
            
            # 保存字幕文件
            video_dir = os.path.dirname(video_path)
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            srt_path = os.path.join(video_dir, f"{video_name}_{language}.srt")
            
            # 写入SRT格式
            try:
                with open(srt_path, 'w', encoding='utf-8') as f:
                    for i, segment in enumerate(segments, 1):
                        start = self.format_srt_time(segment.start)
                        end = self.format_srt_time(segment.end)
                        text = segment.text.strip()
                        if text:  # 只写入非空文本
                            f.write(f"{i}\n{start} --> {end}\n{text}\n\n")
                
                return srt_path
            except Exception as file_err:
                print(f"字幕保存错误: {file_err}")
                self.sub_status.configure(text=f"❌ 字幕保存失败", text_color=COLORS["error"])
                return None
            
        except Exception as e:
            error_msg = str(e)
            print(f"Whisper总体错误: {error_msg}")
            self.sub_status.configure(text="❌ AI生成字幕失败", text_color=COLORS["error"])
            return None
    
    def format_srt_time(self, seconds):
        """格式化SRT时间"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            self.update_status("❌ 请输入视频链接!", COLORS["error"])
            return
        
        if not url.startswith("http"):
            url = "https://" + url
        
        custom_name = self.name_entry.get().strip()
        
        self.download_btn.configure(state="disabled", text="处理中...", fg_color=COLORS["warning"])
        self.progress_bar.set(0)
        
        self.size_label.configure(text="大小: --")
        self.speed_label.configure(text="速度: --")
        self.eta_label.configure(text="剩余: --")
        
        thread = threading.Thread(target=self.download_task, args=(url, custom_name))
        thread.daemon = True
        thread.start()
    
    def download_task(self, url, custom_name):
        downloaded_path = None
        safe_title = "unknown"
        
        try:
            self.update_status("🔍 获取视频信息...") 
            
            # 关键: 确保ffmpeg在PATH中 - 用于合并4K视频和音频
            ffmpeg_path = self.get_ffmpeg_path()
            if ffmpeg_path:
                ffmpeg_dir = os.path.dirname(ffmpeg_path)
                if ffmpeg_dir not in os.environ.get('PATH', ''):
                    os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ.get('PATH', '')
                    print(f"[FFmpeg] Added to PATH: {ffmpeg_dir}")
            
            # 检测平台并应用特殊处理
            is_douyin = 'douyin.com' in url or 'dy.com' in url
            is_youtube = 'youtube.com' in url or 'youtu.be' in url
            
            # 获取画质对应的格式
            quality = self.quality_var.get()
            format_spec = self.get_format_spec(quality)
            
            ydl_opts_info = {
                'quiet': True,
                'no_warnings': True,
                'socket_timeout': 30,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
                },
            }
            
            
            # YouTube 特殊处理 - 让yt-dlp自动处理
            # （注：不添加extractor_args，因为player_client参数会导致高清格式不可用）
            
            # 抖音特殊处理
            if is_douyin:
                ydl_opts_info['extractor_args'] = {
                    'douyin': {
                        'api_hostname': 'api.douyin.com',
                    }
                }
                ydl_opts_info['socket_timeout'] = 60  # 增加超时时间
                ydl_opts_info['http_headers']['Referer'] = 'https://www.douyin.com/'
            
            if self.cookie_file and os.path.exists(self.cookie_file):
                ydl_opts_info['cookiefile'] = self.cookie_file
            
            with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'video').strip()
                ext = info.get('ext', 'mp4')
            
            self.update_status(f"📺 {title[:40]}...")
            self.current_task = title
            
            # 下载配置 - 使用选择的画质
            safe_title = self.sanitize_filename(custom_name or title)
            outtmpl = os.path.join(self.download_dir, f"{safe_title}.%(ext)s")
            
            # 优先使用用户选择的画质
            ydl_opts = {
                'format': format_spec,
                'outtmpl': outtmpl,
                'progress_hooks': [self.progress_hook],
                'noplaylist': True,
                'quiet': True,
                'no_warnings': True,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                    'Referer': 'https://www.douyin.com/' if is_douyin else 'https://www.youtube.com/'
                },
                'extractor_args': {},
                # 字幕下载 - 捕获错误不影响下载
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['zh-CN', 'zh-Hans', 'en', 'zh-TW'],
                'skip_download': False,
                'socket_timeout': 60,
                'postprocessor_args': ['-c:v', 'copy', '-c:a', 'copy'],  # 不重新编码以节省时间
            }
            
            # YouTube 特殊配置 - 启用 Node.js，只使用web player
            
            # YouTube 特殊配置 - 让yt-dlp自动处理
            # （注：不添加extractor_args，因为player_client参数会导致高清格式不可用）
            
            # 抖音特殊配置
            if is_douyin:
                ydl_opts['extractor_args'] = {
                    'douyin': {
                        'api_hostname': 'api.douyin.com',
                    }
                }
                ydl_opts['socket_timeout'] = 90  # 抖音可能需要更多时间
                ydl_opts['download_archive'] = None
                # 抖音不需要字幕
                ydl_opts.pop('writesubtitles', None)
                ydl_opts.pop('writeautomaticsub', None)
                ydl_opts.pop('subtitleslangs', None)
            
            if self.cookie_file and os.path.exists(self.cookie_file):
                ydl_opts['cookiefile'] = self.cookie_file
            
            self.update_status("⬇️ 下载中...")
            
            # 关键修改: 使用 CLI 模式下载而不是 Python API
            # 原因: Python API 中的 js_runtimes 参数无法正确解密签名，导致高清格式不可用
            # CLI 模式通过 --js-runtimes node 参数能正确解密签名和获得所有格式
            
            download_success = False
            try:
                # 构建 yt-dlp CLI 命令
                cmd = ['yt-dlp']
                cmd.extend(['--format', format_spec])
                cmd.extend(['--output', os.path.join(self.download_dir, f"{safe_title}.%(ext)s")])
                cmd.append('--progress')
                cmd.append('--no-warnings')
                cmd.append('--no-playlist')
                cmd.append('-c')  # 允许继续
                
                # FFmpeg 位置 - 关键: 用于合并视频和音频
                ffmpeg_path = self.get_ffmpeg_path()
                if ffmpeg_path:
                    cmd.extend(['--ffmpeg-location', ffmpeg_path])
                    print(f"[FFmpeg] Using: {ffmpeg_path}")
                else:
                    print(f"[WARNING] FFmpeg not found, merging may fail")
                
                # YouTube 特殊处理 - 删除有问题的player_client和js_runtimes参数
                # yt-dlp会自动处理JavaScript和format选择，无需额外配置
                # 添加任何extractor-args都可能导致高清格式不可用
                
                # 抖音特殊处理
                if is_douyin:
                    cmd.extend(['--socket-timeout', '90'])
                    cmd.extend(['--extractor-args', 'douyin:api_hostname=api.douyin.com'])
                
                # Cookie
                if self.cookie_file and os.path.exists(self.cookie_file):
                    cmd.extend(['--cookies', self.cookie_file])
                
                # 其他选项
                cmd.append('--no-check-certificates')
                # 允许继续（恢复部分下载的文件）已在上面添加过
                
                # 强制输出为 MP4 格式，确保合并视频+音频
                # 这样yt-dlp会自动使用ffmpeg合并bestvideo+bestaudio
                cmd.extend(['--merge-output-format', 'mp4'])
                
                # URL
                cmd.append(url)
                
                # 执行 yt-dlp 命令 - 显示所有输出给用户
                print(f"\n[Download] Full Command:")
                print(f"  {' '.join(cmd)}\n")
                print(f"[Download] Selected Quality: {quality}")
                print(f"[Download] Format String: {format_spec}\n")
                
                result = subprocess.run(cmd)
                
                if result.returncode == 0:
                    download_success = True
                    print(f"\n[Success] Download completed")
                else:
                    print(f"\n[Error] yt-dlp returned code: {result.returncode}")
            
            except Exception as download_err:
                print(f"[Error] CLI download error: {download_err}")
                import traceback
                traceback.print_exc()
                # 如果CLI失败，尝试使用Python API作为备选
                try:
                    video_opts = ydl_opts.copy()
                    video_opts.pop('writesubtitles', None)
                    video_opts.pop('writeautomaticsub', None)
                    video_opts.pop('subtitleslangs', None)
                    
                    # 关键: 为Python API指定ffmpeg位置，确保能合并视频音频
                    ffmpeg_path = self.get_ffmpeg_path()
                    if ffmpeg_path:
                        video_opts['ffmpeg_location'] = ffmpeg_path
                        print(f"[API Fallback] Using ffmpeg: {ffmpeg_path}")
                    
                    with yt_dlp.YoutubeDL(video_opts) as ydl:
                        ydl.download([url])
                    download_success = True
                except Exception as api_err:
                    print(f"API 备选也失败: {api_err}")
            
            # 尝试下载字幕 (如果视频下载成功且不是抖音且用户选择了字幕)
            subtitle_choice = self.subtitle_select_var.get()
            if download_success and not is_douyin and subtitle_choice != "无":
                # 根据选择确定语言
                if subtitle_choice == "英文字幕":
                    subtitle_langs = ['en']
                elif subtitle_choice == "中文字幕":
                    subtitle_langs = ['zh-CN', 'zh-Hans']
                else:  # 中英双语
                    subtitle_langs = ['en', 'zh-CN', 'zh-Hans']
                
                for lang in subtitle_langs:
                    try:
                        sub_opts = {
                            'writesubtitles': True,
                            'writeautomaticsub': True,
                            'subtitleslangs': [lang],
                            'skip_download': True,
                            'quiet': True,
                            'no_warnings': True,
                            'outtmpl': os.path.join(self.download_dir, f"{safe_title}.%(ext)s"),
                        }
                        with yt_dlp.YoutubeDL(sub_opts) as ydl:
                            ydl.download([url])
                        print(f"字幕 [{lang}] 下载成功")
                        break
                    except Exception as sub_err:
                        print(f"字幕 [{lang}] 下载失败: {str(sub_err)[:100]}")
                        continue
            
            # 查找文件 - 使用安全的文件名
            base_path = os.path.join(self.download_dir, safe_title)
            downloaded_path = None
            
            # 打印调试信息
            print(f"查找路径: {base_path}.*")
            print(f"下载目录: {self.download_dir}")
            
            # 先精确查找
            for check_ext in ['mp4', 'webm', 'mkv', 'flv']:
                path = f"{base_path}.{check_ext}"
                print(f"检查: {path}, 存在: {os.path.exists(path)}")
                if os.path.exists(path):
                    downloaded_path = path
                    break
            
            # 如果找不到，模糊搜索最近的文件
            if not downloaded_path:
                import glob
                pattern = os.path.join(self.download_dir, f"{safe_title[:10]}*.*")
                print(f"模糊搜索: {pattern}")
                matches = glob.glob(pattern)
                for m in matches:
                    print(f"找到匹配: {m}")
                    if m.lower().endswith(('.mp4', '.webm', '.mkv', '.flv')):
                        downloaded_path = m
                        break
            
            # 如果还没找到，列出最近的文件
            if not downloaded_path:
                import glob
                all_files = glob.glob(os.path.join(self.download_dir, "*.*"))
                video_files = [f for f in all_files if f.lower().endswith(('.mp4', '.webm', '.mkv', '.flv'))]
                print(f"目录下所有文件: {all_files[:10]}")
                print(f"视频文件: {video_files}")
                if video_files:
                    # 返回最近修改的
                    downloaded_path = max(video_files, key=os.path.getmtime)
            
            # 去水印
            if downloaded_path and self.watermark_var.get():
                self.update_status("🧼 去除水印中...")
                no_wm = self.remove_watermark(downloaded_path)
                if no_wm:
                    downloaded_path = no_wm
            
            # 内嵌字幕到视频
            subtitle_choice = self.subtitle_select_var.get()
            if downloaded_path and subtitle_choice != "无":
                self.update_status("📝 内嵌字幕中...")
                with_subs = self.embed_subtitles(downloaded_path, safe_title)
                if with_subs:
                    downloaded_path = with_subs
            
            if downloaded_path:
                self.progress_bar.set(1)
                file_size = os.path.getsize(downloaded_path)
                size_mb = file_size / 1024 / 1024
                self.update_status(f"✅ 下载完成! ({size_mb:.1f}MB)", COLORS["success"])
                self.add_history(f"{safe_title} [{quality}]", "成功")
            else:
                # 文件没找到但可能下载了
                self.update_status("⚠️ 下载完成，但找不到文件", COLORS["warning"])
                self.add_history(f"{safe_title} [未知]", "部分成功")
            
        except Exception as e:
            error = str(e)
            full_error = error
            
            # 更详细的错误识别和处理
            if "JavaScript runtime" in error or "No supported JavaScript" in error:
                full_error = "YouTube需要JavaScript运行库"
            elif "HTTP Error 403" in error or "Not Authorized" in error:
                full_error = "需要VIP或登录! 请设置Cookie"
            elif "Unsupported URL" in error:
                full_error = "不支持的网站，请确保链接正确"
            elif "ffmpeg not found" in error:
                full_error = "需要安装ffmpeg"
            elif "unable to extract" in error.lower():
                full_error = "无法获取视频信息，可能是链接过期或需要登录"
            elif "douyin" in error.lower():
                if "timeout" in error.lower() or "connection" in error.lower():
                    full_error = "抖音连接异常，请检查网络或稍后再试"
                else:
                    full_error = "抖音视频无法下载，可能是链接失效或账号限制"
            elif "rate limit" in error.lower() or "403" in error:
                full_error = "请求过于频繁，请稍候片刻后重试"
            elif "timeout" in error.lower() or "connection" in error.lower():
                full_error = "网络连接超时，请检查网络状态"
            
            display_error = full_error[:50] + "..." if len(full_error) > 50 else full_error
            self.update_status(f"❌ {display_error}", COLORS["error"])
            
            self.last_error = full_error
            self.status_label.bind("<Button-1>", lambda e: self.copy_error())
            self.status_label.configure(cursor="hand2")
            
            self.add_history(safe_title or "未知", "失败")
        
        finally:
            self.download_btn.configure(state="normal", text="⬇️ 开始下载", fg_color=COLORS["primary"])
    
    
    def build_ytdlp_command(self, url, custom_name, format_spec, is_youtube, is_douyin):
        """构建 yt-dlp 命令行参数 - 关键: 支持 JavaScript 运行时和 ffmpeg 合并"""
        cmd = ['yt-dlp']
        
        # 核心参数
        cmd.extend(['--format', format_spec])
        cmd.extend(['--output', os.path.join(self.download_dir, f"{custom_name or '%(title)s'}.%(ext)s")])
        cmd.append('--no-warnings')
        cmd.append('--no-playlist')
        cmd.append('--progress')
        
        # 关键: 指定 ffmpeg 位置 - 用于合并视频和音频 (特别是4K)
        ffmpeg_path = self.get_ffmpeg_path()
        if ffmpeg_path:
            cmd.extend(['--ffmpeg-location', ffmpeg_path])
            print(f"[FFmpeg] Using: {ffmpeg_path}")
        
        # YouTube 特殊处理 - 让yt-dlp自动处理，无需额外参数
        # 添加任何player_client参数都可能导致高清格式不可用
        
        # 抖音特殊处理
        if is_douyin:
            cmd.extend(['--socket-timeout', '90'])
            cmd.extend(['--extractor-args', 'douyin:api_hostname=api.douyin.com'])
        
        # Cookie 支持
        if self.cookie_file and os.path.exists(self.cookie_file):
            cmd.extend(['--cookies', self.cookie_file])
        
        # 其他选项
        cmd.append('--no-check-certificates')
        cmd.append('-c')  # 允许恢复
        
        # 完整输出
        cmd.append(url)
        
        print(f"Running: {' '.join(cmd[:5])}...")
        return cmd
    
    def get_format_spec(self, quality):
        """根据画质选择返回format字符串
        
        关键: 音频必须选择MP4兼容格式(m4a/aac)，避免Opus/WebM格式
        """
        
        # MP4兼容的音频: bestaudio[ext=m4a] 或 bestaudio[acodec^=mp4a]
        # 这样可以避免下载Opus音频导致MP4容器不支持
        mp4_audio = 'bestaudio[ext=m4a]/bestaudio[acodec^=mp4a]/bestaudio'
        
        if quality == "最高":
            # 最高: 优先1080p，降级到720p，最后best (音频必须是MP4兼容)
            return f'(bestvideo[height>=1080]/bestvideo[height>=720])+{mp4_audio}/best'
        elif quality == "4K":
            # 4K优先级: 2160p -> 1440p -> 1080p -> best (音频必须是MP4兼容)
            return f'(bestvideo[height>=2160]/bestvideo[height>=1440]/bestvideo[height>=1080]/bestvideo[height>=720])+{mp4_audio}/best'
        elif quality == "1080P":
            # 1080P: 精确选择1080p，降级到720p，最后best
            return f'(bestvideo[height>=1080]/bestvideo[height>=720])+{mp4_audio}/best'
        elif quality == "720P":
            # 720P: 选择720p，降级到480p，最后best
            return f'(bestvideo[height>=720]/bestvideo[height>=480])+{mp4_audio}/best'
        elif quality == "480P":
            # 480P: 480p或更高，最后best
            return f'(bestvideo[height>=480])+{mp4_audio}/best'
        else:
            return f'(bestvideo[height>=1080]/bestvideo[height>=720])+{mp4_audio}/best'
    
    def sanitize_filename(self, filename):
        """清理文件名中的非法字符"""
        import re
        # 替换Windows不允许的字符
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        # 限制长度
        if len(filename) > 100:
            filename = filename[:100]
        return filename.strip()
    
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            speed = d.get('speed', 0)
            
            if total > 0:
                progress = downloaded / total
                self.progress_bar.set(progress)
                
                size_str = self.format_size(total)
                self.size_label.configure(text=f"大小: {size_str}")
                
                if speed:
                    speed_str = self.format_size(speed) + "/s"
                    self.speed_label.configure(text=f"速度: {speed_str}")
                    
                    remaining = total - downloaded
                    eta_seconds = remaining / speed if speed > 0 else 0
                    eta_str = self.format_time(eta_seconds)
                    self.eta_label.configure(text=f"剩余: {eta_str}")
                
                self.update_status("⬇️ 下载中...")
    
    def get_ffmpeg_path(self):
        """获取ffmpeg路径 - 优先使用本地bin目录"""
        # 先检查本地bin目录
        local_ffmpeg = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin', 'ffmpeg-7.1-essentials_build', 'bin', 'ffmpeg.exe')
        if os.path.exists(local_ffmpeg):
            print(f"使用本地ffmpeg: {local_ffmpeg}")
            return local_ffmpeg
        
        # 再检查系统PATH
        system_ffmpeg = shutil.which('ffmpeg')
        if system_ffmpeg:
            print(f"使用系统ffmpeg: {system_ffmpeg}")
            return system_ffmpeg
    
    def get_nodejs_path(self):
        """获取 Node.js 路径 - yt-dlp 需要完整路径才能识别"""
        import platform
        
        # 首先尝试从 PATH 中找到 Node.js
        node_path = shutil.which('node.exe') or shutil.which('node')
        if node_path:
            print(f"[Node.js] Found in PATH: {node_path}")
            return node_path
        
        # 如果没有在 PATH 中找到，检查标准安装位置
        if platform.system() == 'Windows':
            possible_paths = [
                'C:\\Program Files\\nodejs\\node.exe',
                'C:\\Program Files (x86)\\nodejs\\node.exe',
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    print(f"[Node.js] Found in standard location: {path}")
                    return path
        elif platform.system() == 'Darwin':  # macOS
            possible_paths = [
                '/usr/local/bin/node',
                '/opt/homebrew/bin/node',
                os.path.expanduser('~/.nvm/versions/node/*/bin/node'),
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    print(f"[Node.js] Found in standard location: {path}")
                    return path
        elif platform.system() == 'Linux':
            possible_paths = [
                '/usr/bin/node',
                '/usr/local/bin/node',
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    print(f"[Node.js] Found in standard location: {path}")
                    return path
        
        print("[Node.js] Not found, will try 'node' from PATH")
        return None
    
    def remove_watermark(self, video_path):
        """使用ffmpeg去除水印 - 支持抖音/快手等平台"""
        if not os.path.exists(video_path):
            return None
        
        ffmpeg_path = self.get_ffmpeg_path()
        if not ffmpeg_path:
            print("错误: 未找到ffmpeg")
            return None
        
        name, ext = os.path.splitext(video_path)
        output = f"{name}_no_wm{ext}"
        
        try:
            # 使用crop去除底部水印 (常见于抖音/快手)
            # 去除下面40像素的区域
            cmd = [ffmpeg_path, '-i', video_path, '-vf', 'crop=iw:ih-40:0:0', '-c:a', 'copy', '-c:v', 'libx264', '-preset', 'fast', '-y', output]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0 and os.path.exists(output):
                try:
                    os.remove(video_path)  # 删除原文件
                    print(f"水印去除成功: {output}")
                    return output
                except:
                    return output  # 即使删除失败也返回新文件
        except subprocess.TimeoutExpired:
            print("去水印超时")
        except Exception as e:
            print(f"去水印错误: {e}")
        
        return None
    
    def embed_subtitles(self, video_path, video_title):
        """使用ffmpeg将字幕内嵌到视频中"""
        if not os.path.exists(video_path):
            return None
        
        ffmpeg_path = self.get_ffmpeg_path()
        if not ffmpeg_path:
            print("错误: 未找到ffmpeg")
            return None
        
        # 查找对应的字幕文件
        video_dir = os.path.dirname(video_path)
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        
        # 尝试找字幕文件（支持多种格式）
        subtitle_file = None
        subtitle_formats = ['.vtt', '.srt', '.ass', '.ssa']  # VTT优先，因为YouTube常用
        
        # 等待字幕文件生成（最多等待30秒）
        max_wait = 30
        wait_interval = 0.5
        elapsed = 0
        
        while elapsed < max_wait:
            for fmt in subtitle_formats:
                # 尝试找带_en, _zh等后缀的字幕文件
                for suffix in ['_en', '_zh', '_zh-CN', '_zh-Hans', '']:
                    potential_file = os.path.join(video_dir, f"{video_name}{suffix}{fmt}")
                    if os.path.exists(potential_file):
                        subtitle_file = potential_file
                        print(f"[Subtitles] 找到字幕文件: {os.path.basename(potential_file)}")
                        break
                if subtitle_file:
                    break
            
            if subtitle_file:
                break
            
            # 字幕文件还没生成，等待一下再试
            if elapsed < max_wait - wait_interval:
                print(f"[Subtitles] 等待字幕文件生成... ({elapsed:.1f}s)")
                time.sleep(wait_interval)
                elapsed += wait_interval
            else:
                break
        
        if not subtitle_file:
            print(f"[Subtitles] 未找到字幕文件，跳过内嵌 (等待了{elapsed:.1f}秒)")
            return None
        
        name, ext = os.path.splitext(video_path)
        output = f"{name}_with_subtitle{ext}"
        
        try:
            # 使用ffmpeg的subtitles滤镜将字幕烧录到视频中
            # 这样所有播放器都能看到字幕
            cmd = [
                ffmpeg_path,
                '-i', video_path,
                '-vf', f"subtitles='{subtitle_file}'",  # 烧录字幕到视频
                '-c:a', 'aac',  # 音频编码为AAC
                '-c:v', 'libx264',  # 视频编码为H.264
                '-preset', 'fast',  # 快速编码
                '-y',  # 覆盖输出文件
                output
            ]
            
            print(f"[Subtitles] 开始内嵌字幕: {os.path.basename(subtitle_file)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)
            
            if result.returncode == 0 and os.path.exists(output):
                try:
                    # 删除原视频文件
                    os.remove(video_path)
                    print(f"[Subtitles] 字幕内嵌成功")
                    
                    # 尝试删除字幕文件
                    try:
                        os.remove(subtitle_file)
                        print(f"[Subtitles] 已删除临时字幕文件")
                    except:
                        pass  # 删除失败就忽略
                    
                    return output
                except:
                    return output  # 即使删除失败也返回新文件
            else:
                error_msg = result.stderr[-500:] if result.stderr else "未知错误"
                print(f"[Subtitles] 内嵌失败: {error_msg}")
                return None
        
        except subprocess.TimeoutExpired:
            print("[Subtitles] 内嵌超时")
        except Exception as e:
            print(f"[Subtitles] 错误: {e}")
        
        return None
    
    def update_status(self, text, color=COLORS["text_secondary"]):
        """线程安全的状态更新"""
        try:
            self.status_label.configure(text=text, text_color=color)
            self.update_idletasks()  # 强制刷新UI
        except:
            pass  # 避免线程问题导致崩溃
    
    def add_history(self, title, status):
        """添加下载历史并更新显示"""
        try:
            timestamp = datetime.now().strftime("%H:%M")
            status_icon = "✅" if status == "成功" else "❌"
            record = f"{status_icon} {title[:25]}... [{timestamp}]"
            
            self.download_history.insert(0, record)
            # 最多显示5条
            self.download_history = self.download_history[:5]
            
            display = "\n".join(self.download_history)
            self.history_list.configure(text=display if display else "暂无下载记录")
            
            # 保存到JSON文件用于持久化
            self.save_history()
        except Exception as e:
            print(f"历史记录保存错误: {e}")
    
    def save_history(self):
        """保存历史记录到文件"""
        try:
            import json
            history_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".download_history.json")
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.download_history, f, ensure_ascii=False, indent=2)
        except:
            pass  # 无法保存就跳过
    
    def load_history(self):
        """从文件加载历史记录"""
        try:
            import json
            history_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".download_history.json")
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    self.download_history = json.load(f)[:5]
        except:
            pass  # 无法加载就忽略
    
    def copy_error(self):
        if self.last_error:
            self.clipboard_clear()
            self.clipboard_append(self.last_error)
            self.update_status("✅ 错误已复制!", COLORS["success"])
            self.after(2000, lambda: self.update_status("❌ 点击复制", COLORS["error"]))
    
    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def format_time(self, seconds):
        if seconds < 60:
            return f"{int(seconds)}秒"
        elif seconds < 3600:
            return f"{int(seconds/60)}分"
        else:
            return f"{int(seconds/3600)}小时"


def main():
    app = VideoDownloaderApp()
    app.mainloop()


if __name__ == "__main__":
    main()
