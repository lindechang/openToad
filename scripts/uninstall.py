#!/usr/bin/env python3
"""
卸载脚本 - 清除所有本地数据

运行此脚本将删除 ~/.opentoad/ 目录，包括：
- 记忆体数据
- LLM 配置
- 所有本地存储

此操作不可恢复！
"""

import os
import sys
from pathlib import Path


def main():
    data_dir = Path.home() / ".opentoad"
    
    print("=" * 50)
    print("OpenToad 卸载脚本")
    print("=" * 50)
    print()
    print("此操作将删除以下数据：")
    print(f"  {data_dir}")
    print()
    print("包含：记忆体数据、LLM 配置等")
    print()
    
    if data_dir.exists():
        response = input("确定要删除所有本地数据吗？(y/N): ").strip().lower()
        
        if response == 'y':
            import shutil
            try:
                shutil.rmtree(data_dir)
                print()
                print("✓ 已删除所有本地数据")
                print()
                print("感谢使用 OpenToad！")
            except Exception as e:
                print()
                print(f"✗ 删除失败: {e}")
                sys.exit(1)
        else:
            print()
            print("已取消操作")
    else:
        print("本地数据目录不存在，无需清理")
    
    print()
    print("提示：如果要完全卸载，请删除项目文件夹")


if __name__ == "__main__":
    main()
