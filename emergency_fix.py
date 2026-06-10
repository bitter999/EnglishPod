import json
import os
import requests
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# ================= ⚡️ 配置区域 =================
MODEL_NAME = "qwen2.5:0.5b"
OLLAMA_HOST = "http://localhost:11434" 
SOURCE_DIR = "/home/dizzy/code/my coding/englishpod/skeletons"
RESULT_DIR = "/home/dizzy/code/my coding/englishpod/results"

# ！！！重要：Ollama 本地运行建议总并发控制在 3-5 之间，避免请求堆积导致 Timeout
MAX_WORKERS = 2

SUPER_KNOWLEDGE = """
【重要翻译准则 - 必须严格遵守】
1. 只输出简体中文，禁止输出任何拼音或繁体。
2. 严禁在翻译结果中保留任何英文单词（人名 Marco, Erica, Catherine, Casey 除外）。
3. 语气要极其口语化，像日常聊天一样自然。
4. 术语纠正：
   - press kit -> 新闻资料包
   - extension -> 延期
   - deadline -> 截止日期
   - complimentary -> 免费赠送
   - take the day off -> 请假/休息一天
"""

def is_bad_translation(english, chinese):
    """
    判定翻译质量
    """
    if not chinese or chinese.strip() == "": return True
    chn = str(chinese).strip()
    
    # 1. 包含原本的错误标记
    if "[Conn Error]" in chn: return True
    
    # 2. 复读机检查
    if chn.lower() == str(english).lower(): return True
    
    # 3. 必须包含中文字符
    if not re.search(r'[\u4e00-\u9fff]', chn): return True
    
    # 4. 检查是否依然包含过多的未翻译英文单词（排除人名）
    allowed = {'marco', 'erica', 'catherine', 'casey', 'bill', 'englishpod', 'asap'}
    eng_words = re.findall(r'[a-zA-Z]{4,}', chn) 
    bad_eng_words = [w for w in eng_words if w.lower() not in allowed]
    if len(bad_eng_words) > 1: return True 

    return False

def super_translate(text, session, attempt=1):
    """
    带准则约束的 AI 翻译函数
    """
    # 核心修改：将 SUPER_KNOWLEDGE 注入 System Prompt
    system_prompt = (
        "You are a professional EN-CN translator. "
        "Translate the following English text into conversational Simplified Chinese. "
        f"{SUPER_KNOWLEDGE}\n"
        "Output ONLY the translation result. No explanation."
    )

    payload = {
        "model": MODEL_NAME,
        "prompt": f"{system_prompt}\n\nEnglish: {text}\nChinese:",
        "stream": False,
        "options": {
            "temperature": 0.3 if attempt == 1 else 0.7,
            "num_ctx": 512,
            "stop": ["English:", "Chinese:"] 
        }
    }

    try:
        # 增加超时时间至 45 秒，防止本地模型加载慢导致 Conn Error
        response = session.post(f"{OLLAMA_HOST}/api/generate", json=payload, timeout=45)
        if response.status_code == 200:
            res = response.json().get("response", "").strip()
            
            # 清洗结果：移除可能的引导词和引号
            res = re.sub(r'^(翻译|结果|中文|Chinese)[:：]\s*', '', res).strip()
            res = res.replace('"', '').replace('「', '').replace('」', '')
            
            # 如果翻译质量不合格，自动重试（最多3次）
            if is_bad_translation(text, res) and attempt < 3:
                time.sleep(1)
                return super_translate(text, session, attempt + 1)
            return res
    except Exception as e:
        # 连接失败时自动重试一次
        if attempt < 2: 
            time.sleep(2)
            return super_translate(text, session, attempt + 1)
        return "[Conn Error]" # 最终失败返回标记
    return "[Conn Error]"

def process_single_file(filename):
    src_path = os.path.join(SOURCE_DIR, filename)
    target_path = os.path.join(RESULT_DIR, filename)
    
    # 读取逻辑：如果结果文件夹有文件，读取它进行二次修复；否则读原始文件
    work_path = target_path if os.path.exists(target_path) else src_path
    
    try:
        with open(work_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ 文件打开失败 {filename}: {e}")
        return

    session = requests.Session()
    updated_count = 0
    
    # 筛选出包含 [Conn Error] 或翻译质量差的行
    indices_to_fix = [
        i for i, item in enumerate(data) 
        if is_bad_translation(item.get("english", ""), item.get("chinese", ""))
    ]

    if not indices_to_fix:
        # 如果文件本身就是完好的，且结果目录没文件，则拷贝过去
        if not os.path.exists(target_path):
            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        return

    # 开始逐行修复
    for idx in indices_to_fix:
        original_eng = data[idx]["english"]
        new_chn = super_translate(original_eng, session)
        if new_chn and new_chn != "[Conn Error]":
            data[idx]["chinese"] = new_chn
            updated_count += 1

    # 保存修复后的 JSON
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    if updated_count > 0:
        print(f"✅ {filename}: 修复了 {updated_count} 条数据。")

def main():
    if not os.path.exists(RESULT_DIR): os.makedirs(RESULT_DIR)
    
    files = sorted([f for f in os.listdir(SOURCE_DIR) if f.endswith('.json')])
    
    print(f"🚀 启动修复引擎 | 文件并发: {MAX_WORKERS}")
    print(f"当前翻译模型: {MODEL_NAME}")
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(process_single_file, files)
        
    print("\n🎉 全部处理完成！请运行 generate_js.py 更新前端数据。")

if __name__ == "__main__":
    main()