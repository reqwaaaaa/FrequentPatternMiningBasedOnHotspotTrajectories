import sys
import platform
import subprocess
import os
import secrets


# 要检查的常见 Python 库
COMMON_LIBRARIES = [
    "numpy", "pandas", "matplotlib", "scipy", "sklearn",
    "torch", "tensorflow", "requests", "flask", "django"
]

def check_python_info():
    """ 检查 Python 版本及相关信息 """
    print("="*30)
    print(" Python 环境检测工具 ")
    print("="*30)
    print(f"Python 版本: {sys.version}")
    print(f"Python 可执行路径: {sys.executable}")
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"架构: {platform.architecture()[0]}")
    print("="*30)

def check_pip_version():
    """ 检查 pip 版本 """
    try:
        import pip
        print(f"pip 版本: {pip.__version__}")
    except ImportError:
        print("pip 未安装，请使用 `python -m ensurepip` 安装。")

def check_libraries():
    """ 检查常见的 Python 库是否已安装 """
    print("\n检查常见 Python 库状态:\n")
    for lib in COMMON_LIBRARIES:
        try:
            __import__(lib)
            print(f"[✔] {lib} 已安装")
        except ImportError:
            print(f"[✘] {lib} 未安装")

def list_installed_packages():
    """ 列出已安装的 pip 包 """
    print("\n已安装的 pip 包列表:\n")
    try:
        result = subprocess.run(["pip", "list"], capture_output=True, text=True)
        print(result.stdout)
    except Exception as e:
        print(f"无法获取已安装包列表: {e}")

def test_library_functionality():
    """ 测试部分库的简单功能 """
    print("\n测试库的功能:\n")
    try:
        import numpy as np
        a = np.array([1, 2, 3])
        print(f"[✔] numpy 测试成功: {a}")
    except Exception as e:
        print(f"[✘] numpy 测试失败: {e}")

    try:
        import pandas as pd
        df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        print(f"[✔] pandas 测试成功:\n{df}")
    except Exception as e:
        print(f"[✘] pandas 测试失败: {e}")

    try:
        import matplotlib.pyplot as plt
        plt.plot([1, 2, 3], [4, 5, 6])
        print(f"[✔] matplotlib 测试成功")
    except Exception as e:
        print(f"[✘] matplotlib 测试失败: {e}")

def main():
    check_python_info()
    check_pip_version()
    check_libraries()
    list_installed_packages()
    test_library_functionality()
    path = os.getcwd()
    print(path)
    print(secrets.token_urlsafe(64))
    print(secrets.token_hex(32))   
if __name__ == "__main__":
    main()
