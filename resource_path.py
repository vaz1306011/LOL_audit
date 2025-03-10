import os
import sys


def resource_path(relative_path):
    """獲取打包後的檔案路徑"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return relative_path
