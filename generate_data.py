import json
import os
import re

# ================= ⚙️ 配置区域 =================
# 翻译好的 JSON 文件所在目录
JSON_DIR = "results"

# 音频文件所在目录 (注意：这里只是为了检查文件是否存在)
AUDIO_CHECK_DIR = "assets"

# 最终生成的前端数据目录
DATA_DIR = "data"

# 课程索引文件（轻量，仅包含 ID→标题 映射）
INDEX_FILE = "data_index.js"

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

    # 创建数据目录
    os.makedirs(DATA_DIR, exist_ok=True)

    # 2. 获取所有 JSON 文件并按数字排序
    json_files = [f for f in os.listdir(JSON_DIR) if f.endswith('.json')]
    json_files.sort(key=extract_number)

    custom_titles = load_custom_titles()
    if custom_titles:
        print(f"📝 已加载 {len(custom_titles)} 个自定义标题")

    print(f"🚀 扫描到 {len(json_files)} 个课程文件，开始生成...")

    # 课程索引（轻量数据）
    lesson_index = {}
    total_size = 0

    for filename in json_files:
        # 解析基础信息
        lesson_id = extract_number(filename)
        base_name = os.path.splitext(filename)[0] # 去掉 .json 后缀

        # 3. 构建音频路径
        expected_audio_name = base_name + ".mp3"

        # 检查音频文件是否真的存在
        if os.path.exists(os.path.join(AUDIO_CHECK_DIR, expected_audio_name)):
            final_audio_path = f"./assets/{expected_audio_name}"
            status_icon = "✅"
        else:
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
            "audio": final_audio_path,
            "content": []
        }

        # 提取句子内容
        for item in content_data:
            lesson_data["content"].append({
                "text": item.get("english", ""),
                "trans": item.get("chinese", ""),
                "start": item.get("start", 0),
                "end": item.get("end", 0)
            })

        # 6. 写入单独的课程文件 (data/lesson_1.json, data/lesson_2.json, ...)
        lesson_file = os.path.join(DATA_DIR, f"lesson_{lesson_id}.json")
        with open(lesson_file, "w", encoding="utf-8") as f:
            json.dump(lesson_data, f, ensure_ascii=False, indent=2)

        # 记录文件大小
        file_size = os.path.getsize(lesson_file)
        total_size += file_size

        # 记录索引
        lesson_index[lesson_id] = {
            "title": lesson_data["title"],
            "audio": final_audio_path,
            "size": file_size
        }

        print(f"   {status_icon} 第 {lesson_id} 课 -> {lesson_file} ({file_size/1024:.0f}KB)")

    # 7. 写入课程索引文件（轻量，用于填充下拉菜单）
    index_js = f"window.LESSON_INDEX = {json.dumps(lesson_index, ensure_ascii=False, indent=2)};\n"
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(index_js)

    index_size = os.path.getsize(INDEX_FILE)

    print("-" * 40)
    print(f"🎉 成功生成 {len(lesson_index)} 个课程文件！")
    print(f"📂 数据目录: {DATA_DIR}/")
    print(f"📦 总大小: {total_size/1024/1024:.1f}MB (按需加载)")
    print(f"📋 索引文件: {INDEX_FILE} ({index_size/1024:.0f}KB)")
    print("👉 现在刷新 index.html，手机端也能快速加载！")

if __name__ == "__main__":
    generate_js()