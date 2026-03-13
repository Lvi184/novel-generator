"""
测试 Phase 1 - 完整版本（包含递归摘要）
分析更多章节并测试递归摘要系统
"""
import json
import os
import sys
from pathlib import Path
from openai import OpenAI

# 导入 Phase 1 模块
from phase1_analyzer import (
    NovelSplitter,
    ChapterSummarizer,
    GlobalAnalyzer,
    RecursiveSummarizer,
    save_skeleton,
    save_recursive_summary
)


def main():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    
    print("=" * 60)
    print("Phase 1 - 完整版本测试（含递归摘要）")
    print("=" * 60)
    
    # 读取配置
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 原著路径
    novel_path = config.get("target_novel_path")
    if not novel_path or not os.path.exists(novel_path):
        print(f"[错误] 原著小说不存在：{novel_path}")
        print("请检查 config.json 中的 target_novel_path 配置")
        return
    
    # 创建客户端
    print("\n正在创建客户端...")
    client = OpenAI(
        api_key=config["api_key"],
        base_url=config["base_url"]
    )
    print("客户端创建成功！")
    
    # 输出目录
    output_dir = os.path.join(os.path.dirname(__file__), "data", "analysis_full")
    os.makedirs(output_dir, exist_ok=True)
    
    # Step 1: 分割小说
    print("\n" + "=" * 60)
    print("Step 1: 分割小说")
    print("=" * 60)
    
    splitter = NovelSplitter(novel_path)
    chapters = splitter.split_by_chapters()
    
    # 分析前20章
    max_chapters = min(20, len(chapters))
    test_chapters = chapters[:max_chapters]
    
    print(f"\n将分析前 {max_chapters} 章")
    
    # 保存分割结果
    split_output = os.path.join(output_dir, "chapters_split.json")
    split_data = [
        {"num": c.num, "title": c.title, "content_length": len(c.content)}
        for c in test_chapters
    ]
    with open(split_output, 'w', encoding='utf-8') as f:
        json.dump(split_data, f, ensure_ascii=False, indent=2)
    print(f"分割信息已保存：{split_output}")
    
    # Step 2: 逐章摘要
    print("\n" + "=" * 60)
    print("Step 2: 逐章摘要")
    print("=" * 60)
    
    summarizer = ChapterSummarizer(client, config)
    summaries = []
    
    for chapter in test_chapters:
        summary = summarizer.summarize_chapter(chapter)
        summaries.append(summary)
        print(f"第{summary.num}章: {summary.title} (紧张度: {summary.tension_level}/10)")
    
    # 保存摘要
    summaries_output = os.path.join(output_dir, "chapter_summaries.json")
    summaries_data = [
        {
            "num": s.num,
            "title": s.title,
            "summary": s.summary,
            "characters": s.characters,
            "events": s.events,
            "location": s.location,
            "tension_level": s.tension_level
        }
        for s in summaries
    ]
    with open(summaries_output, 'w', encoding='utf-8') as f:
        json.dump(summaries_data, f, ensure_ascii=False, indent=2)
    print(f"\n章节摘要已保存：{summaries_output}")
    
    # Step 3: 递归摘要
    print("\n" + "=" * 60)
    print("Step 3: 递归摘要金字塔")
    print("=" * 60)
    
    recursive_summarizer = RecursiveSummarizer(client, config)
    recursive_data = recursive_summarizer.build_recursive_summary(
        summaries,
        group_size=5,  # 每5章一组
        max_level=3
    )
    
    # 保存递归摘要
    recursive_output = os.path.join(output_dir, "recursive_summary.json")
    save_recursive_summary(recursive_data, recursive_output)
    
    # 打印全书摘要
    print("\n" + "=" * 60)
    print("全书摘要")
    print("=" * 60)
    print(recursive_data["full_summary"])
    
    # Step 4: 全局分析
    print("\n" + "=" * 60)
    print("Step 4: 全局分析")
    print("=" * 60)
    
    analyzer = GlobalAnalyzer(client, config)
    
    # 分析角色
    characters = analyzer.analyze_characters(summaries)
    print(f"\n分析到 {len(characters)} 个角色:")
    for char in characters:
        print(f"  - {char.name} ({char.narrative_role})")
    
    # 构建骨架
    print("\n正在构建小说骨架...")
    skeleton = analyzer.build_skeleton(test_chapters, summaries)
    
    # 保存骨架
    skeleton_output = os.path.join(output_dir, "novel_skeleton.json")
    save_skeleton(skeleton, skeleton_output)
    
    print("\n" + "=" * 60)
    print("Phase 1 完整测试完成！")
    print(f"分析结果保存在：{output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
