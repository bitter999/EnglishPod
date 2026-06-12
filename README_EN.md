# 🎧 EnglishPod Learning Platform

> An English learning tool based on EnglishPod podcasts, featuring AI-powered transcription, translation, and synchronized subtitle playback

**Language:** [简体中文](README.md) | [English](README_EN.md)

![GitHub](https://img.shields.io/github/license/bitter999/EnglishPod)
![GitHub last commit](https://img.shields.io/github/last-commit/bitter999/EnglishPod)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎧 **Podcast Player** | Play all 365 EnglishPod lessons |
| 📝 **Subtitle Sync** | Real-time highlighting of the current sentence |
| 🔂 **Sentence Loop** | Auto-repeat the current sentence (press `L`) |
| 📌 **A-B Loop** | Loop a custom segment (press `B`) |
| 📖 **Vocabulary Book** | Click words to save, review anytime (press `V`) |
| 🌙 **Dark Mode** | Eye-friendly dark theme (press `D`) |
| ⏭ **Auto Next** | Auto-switch to next lesson when current ends (press `A`) |
| ⌨️ **Keyboard Shortcuts** | `Space` pause · `←→` jump sentences · `C` toggle Chinese · `F` fullscreen |
| 🔊 **Playback Speed** | 0.5× / 1× / 1.5× / 2× |
| 🎨 **Font Size** | Small / Medium / Large / Extra Large |

---

## 🚀 Quick Start

### Online Access (Recommended)

The project is deployed and ready to use:

**http://podcast.cc.cd/**

Works on mobile, tablet, and desktop. No installation needed.

### Local Deployment

To run locally:

```bash
git clone https://github.com/bitter999/EnglishPod.git
cd EnglishPod
python3 -m http.server 8080
# Open http://localhost:8080 in your browser
```

All lesson subtitles and translations are built-in. Audio files may take a moment to load on first access.

---

## 🎯 Recommended Method: Shadowing

> Shadowing is widely recognized as one of the most effective methods for improving English speaking skills, suitable for learners from beginner to advanced.

### Step-by-Step Guide

#### 🔹 Step 1: Blind Listening & Shadowing
**Listen without reading the text, and repeat as simultaneously as possible.**

This step trains your ears to focus on the sounds, rhythm, and intonation of English.

Stop when you can keep up with the audio, or when you feel tired, then move to Step 2.

#### 🔹 Step 2: Read Chinese While Shadowing
**Listen and repeat while looking at the Chinese translation.**

> ⚠️ The time you spend on Step 1 is critical for Step 2. If you only did Step 1 for an hour or less, it will be hard to match the unfamiliar sounds with the Chinese text.

#### 🔹 Step 3: Compare Chinese & English
**Listen and repeat while looking at both Chinese and English text.**

This is a transition step. You may unconsciously focus more on Chinese at first.

Use your finger to point at the text as you read. When you lose your place, your finger helps you find the right sentence instantly.

#### 🔹 Step 4: English-Focused Shadowing
**Listen and repeat, looking at both languages but focusing more on English.**

Build on Step 3 by shifting your attention to the English text, and start trying to understand the English directly.

#### 🔹 Step 5: English-Only Shadowing
**Listen and repeat while looking only at the English text.**

Ears listen to English, mouth repeats English, eyes read English.

At this stage, try an additional exercise: **shadowing while walking**.

### Tips

- Find a place where you can speak aloud — outdoors like a park is ideal
- Wear headphones, hold printed text, stand up straight, and walk briskly
- Shadow the audio, mimicking the rhythm, speed, and intonation as closely as possible
- Beginners should start with suitable material and progress gradually

---

## 📖 Alternative Method: 6-Step Progressive Approach

> If your English foundation is weak, try this 6-step method to learn EnglishPod step by step.

### Step 1: Blind Listening
Listen to the dialogue twice without looking at the text or subtitles.

### Step 2: Listen with Text
While listening with the text:
- Write down unfamiliar phrases
- Highlight words you can see but can't hear
- Note any errors in the official EnglishPod text and check them later

### Step 3: Listen to Explanations & Take Notes
Listen to the EnglishPod hosts' explanations and refine your notes. Look up unknown知识点 (knowledge points) in a dictionary or browser.

> ⚠️ The hosts' explanations may not cover everything. Some specialized topics (piano, medicine, etc.) may require additional research.

### Step 4: Review Notes
Review your notes to reinforce what you've learned.

### Step 5: Re-listen with Notes
Listen to the original dialogue again with your notes. Rewind and replay any parts you still don't understand.

### Step 6: Listen Without Notes
Listen to the original dialogue without any aids. For fast-paced or technical content (sports, weather reports), listen 10–20 times. If still struggling, try again the next day.

### Suggested Pace
Studying 2–3 lessons per day is already quite time-consuming. Take it slow and steady. After completing this process, you'll have built a solid foundation in listening — then you can move on to speaking practice, shadowing, and second-round review.

---

## 🤝 Contributing

Contributions are welcome!

- Submit an Issue for translation errors or feature suggestions
- Pull Requests for code improvements, subtitle fixes, or new features
- Share the project with other English learners

---

## 🔧 Full Workflow (Optional)

If you want to run the transcription and translation pipeline from scratch:

### Prerequisites

```bash
# Install Ollama (local AI translation engine)
curl -fsSL https://ollama.com/install.sh | sudo sh

# Download the translation model
ollama pull qwen2.5:0.5b
```

### Run the Pipeline

```bash
# Step 1: Whisper speech-to-text (requires GPU)
python3 1_gen_skeleton.py

# Step 2: AI translation (English → Chinese)
python3 auto_repair.py

# Step 3: Generate frontend data
python3 generate_data.py
```

---

## 📁 Project Structure

```
├── index.html              # Frontend player
├── data_index.js           # Lesson index (loaded on demand)
├── data/                   # Per-lesson data files
├── README.md               # This file
├── LICENSE                 # MIT License (English)
├── LICENSE_ZH.md           # License (Chinese)
│
├── 1_gen_skeleton.py       # Whisper speech-to-text
├── 2_fill_meat.py          # Ollama translation script
├── auto_repair.py          # Smart translation repair (recommended)
├── generate_data.py        # Generate frontend data files
│
├── assets/                 # MP3 audio files
├── skeletons/              # Whisper transcription output
├── results/                # Translation output
└── .gitignore              # Exclude copyrighted audio from git
```

---

## 💖 Support This Project

If this project helps you learn English, consider:

### ⭐ Star on GitHub

Give a ⭐ star at the top-right corner of the GitHub page — it helps more people discover this project.

### ☕ Buy Me a Coffee

<img width="959" height="772" alt="Donation QR" src="https://github.com/user-attachments/assets/bef30aed-95bf-4a76-a1ed-b8cfd349d6f8" />
<img width="1182" height="1772" alt="Donation QR Alipay" src="https://github.com/user-attachments/assets/e92ef4e8-d748-4bdd-8d2e-ea3d85561807" />

If you'd like, you can buy me a coffee to support continued maintenance and development.

---

## 📜 License

This project is licensed under the **MIT License**. See:
- [English](LICENSE)
- [中文](LICENSE_ZH.md)

**Note:** The MP3 audio files are copyrighted by the original creators of EnglishPod.

---

> Made with ❤️ for English learners