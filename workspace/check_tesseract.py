import subprocess
import sys

try:
    result = subprocess.run(['tesseract', '--version'], capture_output=True, text=True)
    if result.returncode == 0:
        print("Tesseract已安装:")
        print(result.stdout)
    else:
        print("Tesseract未正确安装")
        print("错误:", result.stderr)
except FileNotFoundError:
    print("Tesseract命令未找到，请安装Tesseract OCR引擎")
except Exception as e:
    print(f"检查Tesseract时发生错误: {e}")