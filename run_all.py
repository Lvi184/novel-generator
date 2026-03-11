"""
完整运行脚本
执行整个流程：分析小说 → 生成设定 → 生成目录 → 生成第一章
"""
import os
import sys
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from src.style_analyzer import StyleAnalyzer
from src.narrative_migrator import NarrativeMigrator
from generate_chapter import generate_chapter


def main():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    
    print("=" * 60)
    print("网络小说叙事技法仿写系统")
    print("=" * 60)
    
    # 步骤1：分析小说
    print("\n[步骤 1/4] 分析《多情剑客无情剑》的叙事技法...")
    analyzer = StyleAnalyzer(config_path)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    novel_path = config["target_novel_path"]
    profile_path = os.path.join(config["filepath"], "narrative_profile.json")
    
    if not os.path.exists(profile_path):
        profile = analyzer.analyze_novel(novel_path)
        analyzer.save_profile(profile, profile_path)
    else:
        print("叙事技法档案已存在，跳过分析")
        with open(profile_path, 'r', encoding='utf-8') as f:
            profile = json.load(f)
    
    # 步骤2：生成故事设定
    print("\n[步骤 2/4] 生成故事设定...")
    migrator = NarrativeMigrator(config_path, profile)
    
    setting_path = os.path.join(config["filepath"], "Novel_setting.txt")
    
    if not os.path.exists(setting_path):
        setting = migrator.generate_setting()
        migrator.save_setting(setting, setting_path)
    else:
        print("故事设定已存在，跳过生成")
    
    # 步骤3：生成章节目录
    print("\n[步骤 3/4] 生成章节目录...")
    directory_path = os.path.join(config["filepath"], "Novel_directory.txt")
    
    if not os.path.exists(directory_path):
        directory = migrator.generate_directory(config.get("num_chapters", 120))
        migrator.save_directory(directory, directory_path)
    else:
        print("章节目录已存在，跳过生成")
    
    # 步骤4：生成第一章
    print("\n[步骤 4/4] 生成第一章...")
    chapter_path = os.path.join(config["filepath"], "chapter_1.txt")
    
    if not os.path.exists(chapter_path):
        generate_chapter(config_path, 1)
    else:
        print("第一章已存在，跳过生成")
    
    print("\n" + "=" * 60)
    print("所有步骤完成！")
    print("=" * 60)
    print(f"\n输出文件位置：{config['filepath']}")


if __name__ == "__main__":
    main()
