import subprocess
import time
import sys

# 你的翻译脚本文件名
SCRIPT_NAME = "translate_fix.py" 

def run_script():
    while True:
        print(f"🚀 启动翻译脚本: {SCRIPT_NAME}")
        # 使用 subprocess 运行，捕获退出状态
        process = subprocess.Popen([sys.executable, SCRIPT_NAME])
        process.wait()  # 等待脚本结束（如果崩了，这里会继续往下跑）
        
        if process.returncode == 0:
            print("🎉 翻译任务圆满完成！")
            break
        else:
            print(f"⚠️ 脚本异常退出 (错误码: {process.returncode})，60秒后尝试自动重启...")
            time.sleep(60)

if __name__ == "__main__":
    run_script() 