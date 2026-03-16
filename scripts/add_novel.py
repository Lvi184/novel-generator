#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加新小说工具 - 自动创建目录结构
"""
import os
import sys
from pathlib import Path


def pinyin_slug(chinese_name):
    """简单的中文转拼音（使用映射表，常见小说名）"""
    mappings = {
        "多情剑客无情剑": "duo_qing_jian_ke_wu_qing_jian",
        "回到明朝当王爷": "hui_dao_ming_chao_dang_wang_ye",
        "诛仙": "zhu_xian",
        "斗破苍穹": "dou_po_cang_qiong",
        "武动乾坤": "wu_dong_qian_kun",
        "遮天": "zhe_tian",
        "完美世界": "wan_mei_shi_jie",
        "凡人修仙传": "fan_ren_xiu_xian_zhuan",
        "庆余年": "qing_yu_nian",
        "雪中悍刀行": "xue_zhong_han_dao_xing",
        "我在精神病院学斩神": "xue_zhong_han_dao_xing",
    }
    
    if chinese_name in mappings:
        return mappings[chinese_name]
    
    # 如果没有映射，用简单的替换
    import re
    slug = chinese_name
    slug = re.sub(r'[^\w]', '_', slug)
    return slug


def create_novel_structure(data_dir, novel_name):
    """创建小说目录结构"""
    slug = pinyin_slug(novel_name)
    novel_dir = data_dir / slug
    
    if novel_dir.exists():
        print(f"[警告] 小说目录已存在: {novel_dir}")
        print(f"如需重新创建，请先删除该目录")
        return None
    
    # 创建目录
    subdirs = [
        "input",
        "analysis",
        "analysis_full", 
        "transformed",
        "output",
        "output_enhanced",
        "state"
    ]
    
    novel_dir.mkdir(parents=True, exist_ok=True)
    for subdir in subdirs:
        (novel_dir / subdir).mkdir(parents=True, exist_ok=True)
    
    # 创建说明文件
    readme = novel_dir / "README.txt"
    readme.write_text(f"""小说: {novel_name}
拼音: {slug}
创建时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

使用说明:
1. 将小说TXT文件上传到 input/novel.txt
2. 运行 scripts/test_phase1_full.py 开始分析
""", encoding="utf-8")
    
    print(f"[OK] 成功创建小说目录: {novel_dir}")
    print(f"[目录结构]")
    for subdir in subdirs:
        print(f"   - {subdir}/")
    print(f"\n[下一步] 请将小说文件上传到: {novel_dir / 'input' / 'novel.txt'}")
    
    return novel_dir


def list_novels(data_dir):
    """列出所有小说"""
    print("\n[现有小说列表]")
    novel_dirs = [d for d in data_dir.iterdir() if d.is_dir() and d.name not in ("cache", "src_backup")]
    
    if not novel_dirs:
        print("   (暂无小说)")
        return
    
    for i, novel_dir in enumerate(novel_dirs, 1):
        readme = novel_dir / "README.txt"
        display_name = novel_dir.name
        if readme.exists():
            try:
                lines = readme.read_text(encoding="utf-8").split("\n")
                if lines and lines[0].startswith("小说: "):
                    display_name = lines[0].replace("小说: ", "")
            except:
                pass
        print(f"   {i}. {display_name} ({novel_dir.name}/)")


def main():
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    data_dir = project_dir / "data"
    
    if len(sys.argv) == 1:
        print("""
[小说管理工具]

用法:
  python scripts/add_novel.py list              - 列出所有小说
  python scripts/add_novel.py "小说名称"        - 添加新小说
  
示例:
  python scripts/add_novel.py list
  python scripts/add_novel.py "诛仙"
        """)
        list_novels(data_dir)
        return
    
    command = sys.argv[1]
    
    if command == "list":
        list_novels(data_dir)
    else:
        novel_name = command
        create_novel_structure(data_dir, novel_name)


if __name__ == "__main__":
    main()
