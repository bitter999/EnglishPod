import json
import os
import requests
import re
import time
from tqdm import tqdm  # 引入进度条
from colorama import init, Fore, Style # 引入颜色输出

# 初始化颜色打印
init(autoreset=True)

# ================= ⚡️ 超级 AI 配置 =================
MODEL_NAME = "qwen2.5:0.5b"
OLLAMA_HOST = "http://127.0.0.1:11434"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.join(BASE_DIR, "skeletons")
RESULT_DIR = os.path.join(BASE_DIR, "results")

# 🧠 超级知识库：术语纠正
SUPER_KNOWLEDGE = """
【Terminologies】
Point and shoot = 傻瓜相机
SLR/DSLR = 单反相机
Body = 机身
Lens = 镜头
Telephoto = 长焦
Polarizing filter = 偏振镜
lay down the responsibilities = 卸下重任
vested in = 赋予/授予
Godspeed = 一路顺风
remote and tenuous = 疏远且微弱
steps down = 卸任
resignation letter = 辞职信
entry level = 入门级
display panel = 显示屏
kit lens = 套机镜头
Fluency Builder = 流利构建单元
Global View = 全球视野
"""

def super_translate(text):
    """
    结合了超级知识库的翻译函数
    针对 1.5B 小模型优化了 Prompt，采用 Few-Shot (少样本) 模式，提高稳定性。
    """
    system_prompt = (
        "Role: Professional Translator.\n"
        "Task: Translate English to Simplified Chinese accurately.\n"
        f"{SUPER_KNOWLEDGE}\n"
        "Rules:\n"
        "1. Direct translation only. No explanations.\n"
        "2. Fix specific grammar or context errors based on the list above.\n"
        "Example:\n"
        "English: It's a point and shoot camera.\n"
        "Chinese: 这是一个傻瓜相机。\n"
    )

    payload = {
        "model": MODEL_NAME,
        "prompt": f"{system_prompt}\nEnglish: {text}\nChinese:",
        "stream": False,
        "options": {
            "temperature": 0.1, 
            "num_ctx": 2048,
            "stop": ["\n", "English:", "Translation:"] # 强制停止符，防止模型废话
        }
    }

    try:
        response = requests.post(f"{OLLAMA_HOST}/api/generate", json=payload, timeout=20)
        if response.status_code == 200:
            res = response.json().get("response", "").strip()
            # 清洗残留
            res = re.sub(r'^(Translation|Chinese|翻译|中文|Answer)[:：]\s*', '', res, flags=re.IGNORECASE).strip()
            return res
        return None
    except Exception as e:
        # print(f"API Error: {e}") # 调试时打开
        return None

def run_speed_mission():
    print(Fore.CYAN + f"🚀 启动超级翻译引擎 (Model: {MODEL_NAME})")
    
    if not os.path.exists(RESULT_DIR): 
        os.makedirs(RESULT_DIR)
    
    files = sorted([f for f in os.listdir(SOURCE_DIR) if f.endswith('.json')])
    total_files = len(files)
    
    print(Fore.GREEN + f"📚 准备处理 {total_files} 个文件...")
    
    start_time = time.time()
    processed_files_count = 0
    total_fixed_sentences = 0

    # 使用 tqdm 显示总体进度条
    with tqdm(total=total_files, unit="file", desc="Processing") as pbar:
        for filename in files:
            target_path = os.path.join(RESULT_DIR, filename)
            
            # 优先读取已有结果，支持断点续传/二次修复
            read_path = target_path if os.path.exists(target_path) else os.path.join(SOURCE_DIR, filename)
            
            try:
                with open(read_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                pbar.update(1)
                continue

            dirty = False
            
            # 坏词特征列表
            bad_flags = ["[Conn Error]", "[Error]", "EOF", "点射", "点对点", "身体", "And my name", "翻译："]

            for item in data:
                chn = item.get("chinese", "")
                eng = item.get("english", "")
                
                if not eng: continue

                need_translate = False
                
                # 判定逻辑
                if not chn:
                    need_translate = True
                else:
                    for flag in bad_flags:
                        if flag in str(chn):
                            need_translate = True
                            break
                
                if need_translate:
                    trans = super_translate(eng)
                    if trans:
                        old_chn = chn if chn else "(空)"
                        item["chinese"] = trans
                        dirty = True
                        total_fixed_sentences += 1
                        # 在进度条下方打印修复详情，不破坏进度条显示
                        tqdm.write(f"{Fore.YELLOW}🔧 [{filename}] 修复: {Fore.RESET}{old_chn[:10]}... -> {Fore.GREEN}{trans[:15]}...")

            if dirty:
                with open(target_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                processed_files_count += 1
            
            # 即使没修改，如果目标文件不存在，也要把骨架复制过去
            elif not os.path.exists(target_path):
                 with open(target_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)

            pbar.update(1)

    duration = time.time() - start_time
    print(f"\n" + "="*40)
    print(Fore.GREEN + f"🎉 任务完成！")
    print(f"⏱️ 耗时: {duration:.2f} 秒")
    print(f"📂 修改文件: {processed_files_count} 个")
    print(f"📝 修复句子: {total_fixed_sentences} 行")
    print("="*40)

if __name__ == "__main__":
    run_speed_mission()