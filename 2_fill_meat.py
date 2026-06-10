import json
import os
import requests
import time

# ================= ⚙️ 配置区域 =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.join(BASE_DIR, "skeletons")
RESULT_DIR = os.path.join(BASE_DIR, "results")

# 模型名称 (必须是你 ollama list 里有的)
MODEL_NAME = "qwen2.5:0.5b"
# ==============================================

def check_ollama_status():
    """检查 Ollama 是否启动"""
    try:
        # 尝试连接 WSL 本地
        res = requests.get("http://127.0.0.1:11434", timeout=2)
        if res.status_code == 200:
            print("✅ 成功连接到本地 Ollama (127.0.0.1)")
            return "http://127.0.0.1:11434/api/generate"
    except:
        pass

    # 如果本地连不上，尝试连接 Windows 主机 (针对 WSL 用户)
    try:
        # 获取 Windows IP
        with open("/etc/resolv.conf", "r") as f:
            for line in f:
                if "nameserver" in line:
                    win_ip = line.split()[1]
                    url = f"http://{win_ip}:11434"
                    res = requests.get(url, timeout=2)
                    if res.status_code == 200:
                        print(f"✅ 成功连接到 Windows Ollama ({win_ip})")
                        return f"{url}/api/generate"
    except:
        pass

    return None

def translate_text(api_url, text):
    """调用 Ollama 进行翻译"""
    prompt = (
        "Translate the following English text to Simplified Chinese. "
        "Output ONLY the translation, no explanations.\n\n"
        f"Text: {text}\nTranslation:"
    )
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(api_url, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        else:
            return f"[Error {response.status_code}]"
    except Exception as e:
        return "[Conn Error]"

def batch_process():
    # 1. 检查 Ollama 服务
    api_url = check_ollama_status()
    if not api_url:
        print("\n❌ 错误：连不上 Ollama 服务！")
        print("请确保你已经运行了 'ollama serve'。")
        print("1.如果是 WSL 安装，在终端输入 ollama serve")
        print("2.如果是 Windows 安装，请确保 Windows Ollama 图标已运行")
        return

    # 2. 准备目录
    if not os.path.exists(SOURCE_DIR):
        print(f"❌ 找不到骨架目录: {SOURCE_DIR}")
        return
    if not os.path.exists(RESULT_DIR):
        os.makedirs(RESULT_DIR)

    files = sorted([f for f in os.listdir(SOURCE_DIR) if f.endswith(".json")])
    total_files = len(files)
    print(f"🚀 开始使用本地 AI ({MODEL_NAME}) 翻译 {total_files} 个文件...")

    # 3. 循环处理
    for file_index, filename in enumerate(files):
        target_path = os.path.join(RESULT_DIR, filename)
        source_path = os.path.join(SOURCE_DIR, filename)

        # 优先读取已有结果，支持断点续传
        read_path = target_path if os.path.exists(target_path) else source_path
        
        with open(read_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        file_dirty = False
        
        # 逐句翻译
        for item in data:
            current_chn = item.get("chinese", "")
            
            # 检查是否需要翻译
            if current_chn in ["[Conn Error]", "[Error]", "", None] or "HTTPSConnectionPool" in str(current_chn):
                eng = item.get("english", "")
                if not eng: continue

                print(f"   Generating: {eng[:20]}...")
                trans = translate_text(api_url, eng)
                
                if trans and "[Conn Error]" not in trans:
                    item["chinese"] = trans
                    file_dirty = True
                    print(f"      ✅ {trans[:15]}...")
                else:
                    print("      ❌ 生成失败，跳过")

        # 保存
        if file_dirty:
            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"💾 [{file_index+1}/{total_files}] {filename} 已保存")
        else:
            print(f"⏩ [{file_index+1}/{total_files}] {filename} 无需修改")

    print("\n🎉🎉🎉 全部完成！")

if __name__ == "__main__":
    batch_process()