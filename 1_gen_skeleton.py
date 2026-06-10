import whisper
import json
import os
import torch

# ================= 配置区域 =================
# 使用脚本所在目录作为基准（支持跨设备迁移）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SKELETON_DIR = os.path.join(BASE_DIR, "skeletons")
# 模型选择 (推荐 base 或 medium)
MODEL_SIZE = "base"
# ===========================================

def batch_whisper():
    # 1. 自动创建输出目录
    if not os.path.exists(SKELETON_DIR):
        os.makedirs(SKELETON_DIR)

    # 2. 加载模型
    print(f"🔄 正在加载 Whisper 模型: {MODEL_SIZE}...")
    try:
        model = whisper.load_model(MODEL_SIZE)
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        return

    # 3. 获取所有 MP3 文件并排序
    files = sorted([f for f in os.listdir(ASSETS_DIR) if f.endswith('.mp3')])
    total_files = len(files)
    print(f"📂 扫描到 {total_files} 个音频文件，准备开始处理...")

    # 4. 循环处理
    for index, filename in enumerate(files):
        # 构建路径
        input_path = os.path.join(ASSETS_DIR, filename)
        # 输出文件名：把 .mp3 换成 .json
        output_filename = filename.replace('.mp3', '.json')
        output_path = os.path.join(SKELETON_DIR, output_filename)

        print(f"\n[{index+1}/{total_files}] 正在处理: {filename}")

        # === 核心功能：断点续传 ===
        if os.path.exists(output_path):
            print(f"⏩ 该文件已存在，跳过 (断点续传)。")
            continue
        # ========================

        try:
            # 开始听写
            result = model.transcribe(input_path)
            
            # 提取数据
            skeleton_data = []
            for segment in result["segments"]:
                text = segment["text"].strip()
                if not text: continue
                skeleton_data.append({
                    "start": segment["start"],
                    "end": segment["end"],
                    "english": text,
                    "chinese": "" 
                })

            # 保存单个 JSON
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(skeleton_data, f, indent=4, ensure_ascii=False)
            
            print(f"✅ 已保存: {output_filename}")

        except Exception as e:
            print(f"❌ 处理出错: {filename}, 错误: {e}")

    print("\n🎉 所有听写任务完成！请运行脚本二进行翻译。")

if __name__ == "__main__":
    batch_whisper()