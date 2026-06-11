# 🎧 EnglishPod 英语学习平台

> 一个基于 EnglishPod 播客的英语学习工具，支持 AI 语音转写 + 翻译 + 同步字幕播放

![GitHub](https://img.shields.io/github/license/bitter999/EnglishPod)
![GitHub last commit](https://img.shields.io/github/last-commit/bitter999/EnglishPod)

---

## ✨ 功能

| 功能 | 说明 |
|------|------|
| 🎧 **播客播放器** | 支持 365 课 EnglishPod 课程播放 |
| 📝 **字幕同步高亮** | 实时跟随播放进度高亮当前句子 |
| 🔂 **单句循环** | 自动重复当前句子（快捷键 `L`） |
| 📌 **A-B 循环** | 自选起止点循环播放（快捷键 `B`） |
| 📖 **单词本** | 点击单词收藏，支持复习（快捷键 `V`） |
| 🌙 **深色模式** | 护眼深色主题（快捷键 `D`） |
| ⏭ **自动下一课** | 当前课程结束后自动切换（快捷键 `A`） |
| ⌨️ **快捷键** | `Space` 暂停 · `←→` 切换句子 · `C` 中文 · `F` 全屏 |
| 🔊 **倍速播放** | 0.5× / 1× / 1.5× / 2× |
| 🔍 **课程搜索** | 按课程名实时搜索过滤 |
| 🎨 **字体大小** | 小/中/大/最大 四种字号 |

---

## 🚀 快速开始

### 1. 获取音频文件

本仓库**不包含** EnglishPod 的 MP3 音频文件。请通过合法渠道获取后放入 `assets/` 目录：

```
assets/
├── englishpod_.mp3
├── ...
├── ...
```

### 2. 打开网页

直接用浏览器打开 `index.html` 即可使用（含完整字幕和翻译数据）。

或者启动本地服务器：
```bash
python3 -m http.server 8080
# 浏览器访问 http://localhost:8080
```

---

## 🔧 完整工作流（可选）

如果你想从零开始转写和翻译，需要以下步骤：

### 环境准备

```bash
# 安装 Ollama（本地 AI 翻译引擎）
curl -fsSL https://ollama.com/install.sh | sudo sh

# 下载翻译模型
ollama pull qwen2.5:0.5b
```

### 运行流水线

```bash
# 步骤 1: Whisper 语音转文字（需要 GPU）
python3 1_gen_skeleton.py

# 步骤 2: AI 翻译（英→中）
python3 auto_repair.py

# 步骤 3: 生成前端数据
python3 generate_data.py
```

---

## 📁 项目结构

```
├── index.html              # 前端播放器
├── data.js                 # 字幕 + 翻译数据
├── LICENSE                 # MIT 许可证（英文）
├── LICENSE_ZH.md           # 许可证（中文）
│
├── 1_gen_skeleton.py       # Whisper 语音转文字
├── 2_fill_meat.py          # Ollama 翻译脚本
├── auto_repair.py          # 智能翻译修复（推荐）
├── emergency_fix.py        # 紧急多线程修复
├── generate_data.py        # 合并生成 data.js
├── watchdog.py             # 翻译进程守护
│
├── assets/                 # MP3 音频（自行获取）
├── skeletons/              # Whisper 转写结果
├── results/                # 翻译结果
└── .gitignore              # 排除有版权的音频
```

---

## 📜 许可证

本项目使用 **MIT 许可证**，详情请查看：
- [English](LICENSE)
- [中文](LICENSE_ZH.md)

**注意：** MP3 音频文件版权归 EnglishPod 原作者所有。

---

> Made with ❤️ for English learners
