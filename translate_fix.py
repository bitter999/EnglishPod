#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高质量翻译修复脚本 - qwen2.5:0.5b 优化版
- 多种 prompt 策略自动重试
- 智能质量检测
- 断点续传
"""
import json, os, requests, re, time, sys

MODEL_NAME = "qwen2.5:0.5b"
OLLAMA_HOST = "http://127.0.0.1:11434"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULT_DIR = os.path.join(BASE_DIR, "results")
MAX_RETRIES = 3

def is_bad(text):
    """宽松质量检查 - 只要有中文字符且没明显错误就接受"""
    if not text or text == "[Conn Error]" or text == "[Error]":
        return True

    # 模型拒绝回答或要求提供更多信息
    hard_bad = [
        "请提供", "请确认", "请给出",
        "对不起，我不能", "抱歉，我无法",
        "作为一个AI", "作为一个语言模型",
        "我是一个AI", "我是一个语言模型",
        "我不确定你的", "我不知道你在",
    ]
    for flag in hard_bad:
        if flag in text:
            return True

    # 以"英语："、"English:"、"Translation:"等开头 - 说明模型没翻译
    if re.match(r'^(English|翻译|Translation|Chinese|Answer)[:：]', text, re.IGNORECASE):
        return True

    # 必须包含至少一个中文字符
    chinese_chars = re.findall(r'[一-鿿]', text)
    if len(chinese_chars) == 0:
        return True

    # 中文占比不低于 5%
    if len(chinese_chars) / max(len(text), 1) < 0.05:
        return True

    return False

def clean(text):
    if not text:
        return ""
    text = re.sub(r'^(Translation|Chinese|翻译|中文|Answer)[:：]\s*', '', text, flags=re.IGNORECASE).strip()
    text = text.strip('"\'"\'""''')
    return text.strip()

def translate(english_text, attempt=0):
    """调用 Ollama，不同尝试用不同 prompt"""
    prompts = [
        # 策略1: 最简洁直接
        f"Translate to Chinese:\n{english_text}\nChinese:",
        # 策略2: 示例引导
        f"English: {english_text}\nChinese:",
        # 策略3: 中文指令
        f"把下面这句英文翻译成中文:\n{english_text}\n中文:",
    ]
    
    prompt = prompts[min(attempt, len(prompts)-1)]
    temp = 0.05 + (attempt * 0.1)  # 重试时略微提高温度
    
    try:
        payload = {
            "model": MODEL_NAME, "prompt": prompt, "stream": False,
            "options": {"temperature": temp, "num_ctx": 2048, "stop": ["\n", "English:", "Chinese:"]}
        }
        r = requests.post(f"{OLLAMA_HOST}/api/generate", json=payload, timeout=30, proxies={"http": None, "https": None})
        if r.status_code == 200:
            result = r.json().get("response", "").strip()
            return clean(result)
    except:
        pass
    return None

def main():
    print(f"🚀 智能翻译引擎 ({MODEL_NAME})", flush=True)
    print(f"📂 目录: {RESULT_DIR}", flush=True)
    
    if not os.path.exists(RESULT_DIR):
        print("❌ 找不到目录"); sys.exit(1)
    
    files = sorted([f for f in os.listdir(RESULT_DIR) if f.endswith('.json')])
    total_fixed = 0; total_files = 0; total_skipped = 0
    
    for idx, filename in enumerate(files):
        filepath = os.path.join(RESULT_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 只处理包含 [Conn Error] 的文件
        conn_indices = [i for i, item in enumerate(data) if item.get("chinese", "").strip() == "[Conn Error]"]
        if not conn_indices:
            total_skipped += 1
            if (idx+1) % 20 == 0:
                print(f"  📊 进度: {idx+1}/{len(files)} | 已修复 {total_fixed} 句 | 跳过 {total_skipped} 文件", flush=True)
            continue

        dirty = False; file_fixed = 0

        for i in conn_indices:
            eng = data[i].get("english", "").strip()
            if not eng:
                continue

            # 多轮重试翻译
            translation = None
            for attempt in range(MAX_RETRIES):
                translation = translate(eng, attempt)
                if translation and not is_bad(translation):
                    break
                if attempt < MAX_RETRIES - 1:
                    time.sleep(0.5)

            if translation and not is_bad(translation):
                data[i]["chinese"] = translation
                dirty = True; file_fixed += 1
                print(f"  ✅ [{idx+1}/{len(files)}] {filename}: \"{eng[:30]}...\" -> \"{translation[:35]}...\"", flush=True)
            else:
                reason = translation[:25] if translation else "None"
                print(f"  ❌ [{idx+1}/{len(files)}] {filename}: 失败 ({reason})", flush=True)

        if dirty:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            total_files += 1; total_fixed += file_fixed

        if (idx+1) % 10 == 0 or idx == len(files)-1:
            print(f"  📊 进度: {idx+1}/{len(files)} | 已修复 {total_fixed} 句 | 修改 {total_files} 文件", flush=True)
    
    print(f"\n{'='*40}")
    print(f"✅ 完成！修复 {total_fixed} 句，修改 {total_files} 文件，跳过 {total_skipped} 文件")
    print(f"{'='*40}")

if __name__ == "__main__":
    main()
