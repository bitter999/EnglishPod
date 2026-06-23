#!/usr/bin/env python3
"""
批量高质量翻译脚本 - 重新翻译所有 365 课 EnglishPod 内容
使用 qwen2.5:3b (优先) 或 qwen2.5:0.5b (备用)
支持断点续传，多进程并行
"""
import json, os, requests, re, time, sys
from concurrent.futures import ThreadPoolExecutor, as_completed

MODEL_3B = "qwen2.5:3b"
MODEL_05B = "qwen2.5:0.5b"
OLLAMA_HOST = "http://127.0.0.1:23456"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SKELETON_DIR = os.path.join(BASE_DIR, "skeletons")
RESULT_DIR = os.path.join(BASE_DIR, "results")
MAX_WORKERS = 3  # 并发数

# ============ 术语知识库 ============
KNOWLEDGE_BASE = """【专业术语翻译对照 - 必须遵守】
tattoo = 纹身
nail art / manicure = 美甲
press kit = 新闻资料包
extension = 延期
deadline = 截止日期
complimentary = 免费赠送
take the day off = 请假/休息一天
point and shoot = 傻瓜相机
SLR / DSLR = 单反相机
body (camera) = 机身
lens = 镜头
telephoto = 长焦
polarizing filter = 偏振镜
lay down the responsibilities = 卸下重任
vested in = 赋予/授予
Godspeed = 一路顺风
remote and tenuous = 疏远且微弱
steps down = 卸任
resignation letter = 辞职信
entry level = 入门级
kit lens = 套机镜头
Fluency Builder = 流利构建单元
Global View = 全球视野
elementary = 初级
intermediate = 中级
upper intermediate = 中高级
advanced = 高级
"""

def get_best_model():
    """检测可用模型，优先使用 3b"""
    try:
        r = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
        if r.status_code == 200:
            models = [m["name"] for m in r.json().get("models", [])]
            if MODEL_3B in models:
                print(f"✅ 使用模型: {MODEL_3B}")
                return MODEL_3B
            elif MODEL_05B in models:
                print(f"⚠️ 使用模型: {MODEL_05B}（推荐 qwen2.5:3b 以获得更好质量）")
                return MODEL_05B
    except:
        pass
    print("❌ 无法连接到 Ollama")
    sys.exit(1)

def translate_sentence(model, text):
    """翻译单个句子"""
    prompt = f"""You are a professional English-to-Chinese translator. Follow these rules:
1. Translate accurately and naturally
2. Output ONLY the Chinese translation, no explanations or extra text
3. Use the terminology guide below:
{KNOWLEDGE_BASE}

English: {text}
Chinese:"""

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_ctx": 2048,
            "stop": ["\n", "English:", "Chinese:", "Translation:"]
        }
    }

    try:
        r = requests.post(f"{OLLAMA_HOST}/api/generate", json=payload, timeout=60)
        if r.status_code == 200:
            res = r.json().get("response", "").strip()
            # 清洗结果
            res = re.sub(r'^(Translation|Chinese|翻译|中文|Answer)[:：]\s*', '', res, flags=re.IGNORECASE).strip()
            res = res.strip('"\'""''')
            return res
    except:
        pass
    return None

def is_translation_good(english, chinese):
    """判断翻译质量"""
    if not chinese or not chinese.strip():
        return False
    if chinese.strip() in ["[Conn Error]", "[Error]", ""]:
        return False
    # 必须包含中文字符
    if not re.search(r'[一-鿿]', chinese):
        return False
    # 不应该和原文一模一样（说明没翻译）
    if chinese.lower().strip() == str(english).lower().strip():
        return False
    return True

def process_file(model, filename):
    """处理单个文件"""
    src_path = os.path.join(SKELETON_DIR, filename)
    target_path = os.path.join(RESULT_DIR, filename)

    if not os.path.exists(src_path):
        return filename, 0, "skeleton not found"

    try:
        with open(src_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return filename, 0, f"read error: {e}"

    total = len(data)
    updated = 0
    errors = 0

    for i, item in enumerate(data):
        eng = item.get("english", "").strip()
        if not eng:
            continue

        # 重试最多 3 次
        translation = None
        for attempt in range(3):
            translation = translate_sentence(model, eng)
            if translation and is_translation_good(eng, translation):
                break
            time.sleep(0.3)

        if translation and is_translation_good(eng, translation):
            data[i]["chinese"] = translation
            updated += 1
        else:
            data[i]["chinese"] = translation or "[Error]"
            errors += 1

        # 每 20 句打印进度
        if (i + 1) % 20 == 0 or i == total - 1:
            print(f"  [{filename}] {i+1}/{total} | 成功: {updated} | 失败: {errors}", flush=True)

    # 保存
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return filename, updated, errors

def get_todo_files():
    """读取待翻译文件列表，支持断点续传"""
    todo_file = "/tmp/todo_translate.txt"
    if os.path.exists(todo_file):
        with open(todo_file) as f:
            todo = [line.strip() for line in f if line.strip()]
        if todo:
            print(f"📋 从待处理列表加载: {len(todo)} 个文件")
            return todo
    return None

def main():
    model = get_best_model()
    print(f"📂 翻译目录: {SKELETON_DIR}")
    print(f"💾 输出目录: {RESULT_DIR}")

    if not os.path.exists(RESULT_DIR):
        os.makedirs(RESULT_DIR)

    # 支持断点续传：优先从 todo list 加载
    todo_files = get_todo_files()
    if todo_files:
        files = todo_files
    else:
        files = sorted([f for f in os.listdir(SKELETON_DIR) if f.endswith(".json")])

    if not files:
        print("❌ 找不到待翻译文件")
        sys.exit(1)

    print(f"📚 待翻译: {len(files)} 个文件")
    print(f"⚡ 并发: {MAX_WORKERS}")
    print("=" * 50)

    # 统计所有句子
    total_sentences = 0
    for fn in files:
        fp = os.path.join(SKELETON_DIR, fn)
        if os.path.exists(fp):
            with open(fp) as f:
                total_sentences += len(json.load(f))
    print(f"📝 总句子数: {total_sentences}")
    print("=" * 50)

    start_time = time.time()
    completed = 0
    total_updated = 0
    total_errors = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_file, model, fn): fn for fn in files}

        for future in as_completed(futures):
            fn, updated, errors = future.result()
            completed += 1
            total_updated += updated
            total_errors += errors
            elapsed = time.time() - start_time
            rate = completed / elapsed * 60  # files per minute
            eta = (len(files) - completed) / max(rate, 0.1)
            print(f"\n✅ [{completed}/{len(files)}] {fn} | +{updated}句 | 耗时: {elapsed:.0f}s | 预计剩余: {eta:.0f}s")
            # 实时更新进度
            completed_pct = completed * 100 / len(files)
            elapsed_min = elapsed / 60
            eta_min = eta / 60
            print(f"   📊 进度: {completed_pct:.1f}% | 已跑: {elapsed_min:.0f}min | 预计剩余: {eta_min:.0f}min")

    duration = time.time() - start_time
    print("\n" + "=" * 50)
    print(f"🎉 全部完成！")
    print(f"⏱️ 总耗时: {duration:.0f}s ({duration/60:.1f}min)")
    print(f"📂 处理文件: {completed}")
    print(f"📝 更新句子: {total_updated}")
    print(f"❌ 失败句子: {total_errors}")
    print(f"📊 平均速度: {total_sentences/duration:.1f} 句/秒")
    print("=" * 50)
    # 清理 todo 文件
    if os.path.exists("/tmp/todo_translate.txt"):
        os.remove("/tmp/todo_translate.txt")

if __name__ == "__main__":
    main()