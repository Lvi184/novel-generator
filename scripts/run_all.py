"""
运行整个小说仿写系统
"""
import os
import json
from pathlib import Path
from openai import OpenAI

from src.core.config_loader import config
from src.core.llm_adapter import create_llm_adapter
from src.core.state_tracker import StateTracker
from src.analysis.splitter import NovelSplitter
from src.analysis.summarizer import ChapterSummarizer
from src.analysis.analyzer import GlobalAnalyzer, save_skeleton
from src.analysis.recursive import RecursiveSummarizer, save_recursive_summary
from src.transformation.transformer import SkeletonTransformer, save_transformed_outline
from src.generation.chapter_generator import EnhancedChapterGenerator, save_enhanced_chapter


def main():
    """主函数"""
    print("=" * 80)
    print("小说仿写系统")
    print("=" * 80)
    
    # 1. 初始化配置和客户端
    print("\n1. 初始化配置和客户端...")
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        print("错误：请设置 DEEPSEEK_API_KEY 环境变量")
        return
    
    client = OpenAI(
        base_url=config.get("model.base_url"),
        api_key=api_key,
        timeout=config.get("model.timeout")
    )
    
    # 2. 准备输入输出路径
    input_novel = "data/input/target_novel/多情剑客无情剑.txt"
    analysis_dir = config.get("paths.analysis")
    analysis_full_dir = config.get("paths.analysis_full")
    transformed_dir = config.get("paths.transformed")
    output_dir = config.get("paths.output")
    output_enhanced_dir = config.get("paths.output_enhanced")
    
    # 创建目录
    for directory in [analysis_dir, analysis_full_dir, transformed_dir, output_dir, output_enhanced_dir]:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # 3. Phase 1: 深度解剖
    print("\n2. Phase 1: 深度解剖...")
    
    # 3.1 分割章节
    print("  2.1 分割章节...")
    splitter = NovelSplitter(input_novel)
    chapters = splitter.split_by_chapters()
    
    # 3.2 逐章摘要
    print("  2.2 逐章摘要...")
    summarizer = ChapterSummarizer(client)
    summaries = []
    for chapter in chapters[:10]:  # 只处理前10章作为示例
        summary = summarizer.summarize_chapter(chapter)
        summaries.append(summary)
    
    # 3.3 全局分析
    print("  2.3 全局分析...")
    analyzer = GlobalAnalyzer(client)
    skeleton = analyzer.build_skeleton(chapters, summaries)
    
    # 3.4 保存骨架
    skeleton_path = os.path.join(analysis_dir, "novel_skeleton.json")
    save_skeleton(skeleton, skeleton_path)
    
    # 3.5 递归摘要
    print("  2.4 递归摘要...")
    recursive_summarizer = RecursiveSummarizer(client)
    recursive_summary = recursive_summarizer.build_recursive_summary(summaries)
    recursive_path = os.path.join(analysis_full_dir, "recursive_summary.json")
    save_recursive_summary(recursive_summary, recursive_path)
    
    # 4. Phase 2: 骨架变形
    print("\n3. Phase 2: 骨架变形...")
    
    # 4.1 准备新故事设定
    new_story = {
        "genre": "都市重生",
        "setting": {
            "background": "2010年深圳互联网创业潮",
            "time": "2010年",
            "location": "深圳"
        },
        "protagonist": {
            "name": "林风",
            "age": 28,
            "occupation": "程序员",
            "trait": "重情义，聪明，有商业头脑"
        }
    }
    
    # 4.2 执行变形
    transformer = SkeletonTransformer(client)
    transformed_outline = transformer.transform(skeleton_path, new_story, num_chapters=10)
    
    # 4.3 保存新大纲
    outline_path = os.path.join(transformed_dir, "transformed_outline.json")
    save_transformed_outline(transformed_outline, outline_path)
    
    # 5. Phase 3: 逐章生成
    print("\n4. Phase 3: 逐章生成...")
    
    # 5.1 初始化状态追踪器
    state_tracker = StateTracker()
    
    # 5.2 初始化章节生成器
    generator = EnhancedChapterGenerator(client, state_tracker)
    
    # 5.3 逐章生成
    previous_chapters = []
    for i, chapter_outline in enumerate(transformed_outline.chapter_outlines):
        chapter_num = i + 1
        print(f"  4.3 生成第{chapter_num}章...")
        
        # 生成章节
        content, quality = generator.generate_chapter_with_quality(
            chapter_num, chapter_outline, previous_chapters
        )
        
        # 保存章节
        save_enhanced_chapter(chapter_num, content, quality, output_enhanced_dir)
        
        # 更新状态
        previous_chapters.append(content)
        
        # 添加角色到状态追踪器
        for char_name in chapter_outline.get("characters", []):
            if not state_tracker.get_character(char_name):
                state_tracker.add_character(
                    name=char_name,
                    location=chapter_outline.get("location", ""),
                    emotion="",
                    injury="",
                    inventory=[]
                )
        
        # 模拟添加一些状态
        if chapter_num == 1:
            state_tracker.add_foreshadowing(1, "林风发现iPhone中的未来知识")
        elif chapter_num == 3:
            state_tracker.resolve_foreshadowing(3, "林风发现iPhone中的未来知识")
    
    print("\n" + "=" * 80)
    print("小说仿写系统运行完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()
