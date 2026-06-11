import json
import os
import re

# ================= ⚙️ 配置区域 =================
# 翻译好的 JSON 文件所在目录
JSON_DIR = "results"

# 音频文件所在目录 (注意：这里只是为了检查文件是否存在)
AUDIO_CHECK_DIR = "assets"

# 最终生成的 JS 文件
OUTPUT_FILE = "data.js"

# 自定义标题文件（你可以在这里改课程名）
CUSTOM_TITLES_FILE = "custom_titles.json"
# ==============================================

def load_custom_titles():
    """加载自定义标题，返回 { lesson_id: title } 字典"""
    if os.path.exists(CUSTOM_TITLES_FILE):
        try:
            with open(CUSTOM_TITLES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  读取自定义标题文件失败: {e}")
    return {}

def extract_number(filename):
    """
    从文件名中提取数字用于排序
    例如: "englishpod_001pb.json" -> 1
    解决 "1, 10, 11... 2" 这种排序错误
    """
    match = re.search(r'(\d+)', filename)
    return int(match.group(1)) if match else 999999

def generate_js():
    # 1. 检查文件夹是否存在
    if not os.path.exists(JSON_DIR):
        print(f"❌ 错误：找不到翻译文件夹 '{JSON_DIR}'")
        return
    if not os.path.exists(AUDIO_CHECK_DIR):
        print(f"❌ 错误：找不到音频文件夹 '{AUDIO_CHECK_DIR}'")
        return

    # 2. 获取所有 JSON 文件并按数字排序
    json_files = [f for f in os.listdir(JSON_DIR) if f.endswith('.json')]
    json_files.sort(key=extract_number)

    custom_titles = load_custom_titles()
    if custom_titles:
        print(f"📝 已加载 {len(custom_titles)} 个自定义标题")

    print(f"🚀 扫描到 {len(json_files)} 个课程文件，开始生成 data.js...")

    global_data = {}

    for filename in json_files:
        # 解析基础信息
        lesson_id = extract_number(filename)
        base_name = os.path.splitext(filename)[0] # 去掉 .json 后缀
        
        # 3. 构建音频路径
        # 我们假设音频文件名和 JSON 文件名是一样的 (只差后缀)
        # 例如: json 是 englishpod_001pb.json -> 音频是 englishpod_001pb.mp3
        expected_audio_name = base_name + ".mp3"
        
        # 检查音频文件是否真的存在
        if os.path.exists(os.path.join(AUDIO_CHECK_DIR, expected_audio_name)):
            # ★★★ 核心修复：必须使用相对路径 "./assets/" ★★★
            # 只有这样，index.html 才能通过浏览器访问到它
            final_audio_path = f"./assets/{expected_audio_name}"
            status_icon = "✅"
        else:
            # 如果找不到音频，给一个空路径或者警告
            print(f"⚠️  警告：第 {lesson_id} 课找不到音频文件: {expected_audio_name}")
            final_audio_path = "" 
            status_icon = "⚠️ "

        # 4. 读取 JSON 内容
        file_path = os.path.join(JSON_DIR, filename)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content_data = json.load(f)
        except Exception as e:
            print(f"❌ 读取文件 {filename} 失败: {e}")
            continue

        # 5. 组装成前端需要的数据格式
        lesson_data = {
            "title": custom_titles.get(str(lesson_id), base_name),
            "audio": final_audio_path, # 这里存进去的是 ./assets/xxx.mp3
            "content": []
        }

        # 提取句子内容
        for item in content_data:
            lesson_data["content"].append({
                "text": item.get("english", ""),
                "trans": item.get("chinese", ""), # 你的翻译内容
                "start": item.get("start", 0),    # 时间轴 (如果有)
                "end": item.get("end", 0)
            })

        # 存入大字典
        global_data[lesson_id] = lesson_data
        print(f"   {status_icon} 处理完毕: 第 {lesson_id} 课 -> 音频路径: {final_audio_path}")

    # 6. 写入 data.js
    # 格式：window.GLOBAL_DATA = { ... };
    js_content = f"window.GLOBAL_DATA = {json.dumps(global_data, ensure_ascii=False, indent=4)};"
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(js_content)

    print("-" * 40)
    print(f"🎉 成功生成 {OUTPUT_FILE}！")
    print(f"📂 包含课程数量: {len(global_data)}")
    print("👉 现在刷新 index.html，音频应该可以播放了！")

if __name__ == "__main__":
    generate_js()