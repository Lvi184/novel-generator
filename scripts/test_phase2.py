"""
测试 Phase 2 - 骨架变形模块
将古龙原著骨架变形为都市重生设定
"""
import json
import os
import sys
from pathlib import Path
from openai import OpenAI

# 导入 Phase 2 模块
from phase2_transformer import (
    SkeletonTransformer,
    save_transformed_outline
)


def main():
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
    
    print("=" * 60)
    print("Phase 2 - 骨架变形模块测试")
    print("=" * 60)
    
    # 读取配置
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 原著骨架路径
    skeleton_path = os.path.join(
        os.path.dirname(__file__),
        "..", "data", "xue_zhong_han_dao_xing", "analysis_full", "novel_skeleton.json"
    )
    
    if not os.path.exists(skeleton_path):
        print(f"[错误] 原著骨架不存在：{skeleton_path}")
        print("请先运行 test_phase1_full.py 生成原著骨架")
        return
    
    # 新故事设定
    new_story = config.get("new_story", {})
    
    print("\n新故事设定：")
    print(f"  类型：{new_story.get('genre', '')}")
    print(f"  核心创意：{new_story.get('core_idea', '')}")
    print(f"  主角：{new_story.get('protagonist', {}).get('name', '')}")
    print(f"  背景：{new_story.get('setting', {}).get('background', '')}")
    
    # 创建客户端
    print("\n正在创建客户端...")
    client = OpenAI(
        api_key=config["api_key"],
        base_url=config["base_url"]
    )
    print("客户端创建成功！")
    
    # 输出目录
    output_dir = os.path.join(os.path.dirname(__file__), "..", "data", "xue_zhong_han_dao_xing", "transformed")
    os.makedirs(output_dir, exist_ok=True)
    
    # 执行骨架变形
    transformer = SkeletonTransformer(client, config)
    outline = transformer.transform(
        original_skeleton_path=skeleton_path,
        new_story=new_story,
        num_chapters=20
    )
    
    # 保存结果
    outline_output = os.path.join(output_dir, "transformed_outline.json")
    save_transformed_outline(outline, outline_output)
    
    # 打印概要
    print("\n" + "=" * 60)
    print("变形结果概要")
    print("=" * 60)
    
    print(f"\n世界观映射：{len(outline.world_mappings)} 个")
    for wm in outline.world_mappings[:5]:
        print(f"  - {wm.original_element} → {wm.new_element}")
    if len(outline.world_mappings) > 5:
        print(f"  ... 还有 {len(outline.world_mappings) - 5} 个")
    
    print(f"\n角色映射：{len(outline.character_mappings)} 个")
    for cm in outline.character_mappings:
        print(f"  - {cm.original_name} ({cm.original_role}) → {cm.new_name} ({cm.new_role})")
    
    print(f"\n剧情节拍映射：{len(outline.beat_mappings)} 个")
    for bm in outline.beat_mappings[:3]:
        print(f"  - {bm.original_description[:30]}... → {bm.new_description[:30]}...")
    if len(outline.beat_mappings) > 3:
        print(f"  ... 还有 {len(outline.beat_mappings) - 3} 个")
    
    print(f"\n章节大纲：{len(outline.chapter_outlines)} 章")
    for co in outline.chapter_outlines[:5]:
        print(f"  第{co.get('chapter_num', '')}章：{co.get('title', '')}")
    if len(outline.chapter_outlines) > 5:
        print(f"  ... 还有 {len(outline.chapter_outlines) - 5} 章")
    
    print("\n" + "=" * 60)
    print("Phase 2 测试完成！")
    print(f"结果保存在：{outline_output}")
    print("=" * 60)


if __name__ == "__main__":
    main()
