"""
测试 Phase 3 - 增强版逐章生成模块
测试记忆系统、质量检查、自动重试、章节衔接优化
"""
import json
import os
import sys
from pathlib import Path
from openai import OpenAI

# 导入模块
from state_tracker import StateTracker, CharacterState, Relationship
from phase3_generator import (
    EnhancedChapterGenerator,
    save_enhanced_chapter
)


def init_test_state_tracker(config: dict) -> StateTracker:
    """初始化测试用的状态追踪器"""
    save_dir = os.path.join(os.path.dirname(__file__), "data", "state_test")
    tracker = StateTracker(save_dir=save_dir)
    
    # 清空并重新初始化
    tracker.characters.clear()
    tracker.relationships.clear()
    tracker.foreshadows.clear()
    tracker.timeline.clear()
    tracker.knowledges.clear()
    tracker.current_chapter = 0
    tracker.current_day = 1
    
    # 删除旧状态文件
    state_file = Path(save_dir) / "state.json"
    if state_file.exists():
        state_file.unlink()
    
    # 林风
    linfeng = CharacterState(
        name="林风",
        location="深圳出租屋",
        emotion="震惊",
        injury="无",
        inventory=["iPhone 15 Pro Max", "钱包", "钥匙"],
        personality="聪明、低调、重情义，性格坚韧",
        speech_style="平时话不多，关键时刻很坚定"
    )
    tracker.add_character(linfeng)
    
    # 苏晴
    suqing = CharacterState(
        name="苏晴",
        location="深圳",
        emotion="温柔",
        injury="无",
        personality="温柔体贴，支持林风",
        speech_style="语气温柔，善解人意"
    )
    tracker.add_character(suqing)
    
    # 李磊
    lilei = CharacterState(
        name="李磊",
        location="深圳",
        emotion="热情",
        injury="无",
        personality="讲义气，古道热肠",
        speech_style="大大咧咧，很直接"
    )
    tracker.add_character(lilei)
    
    # 古野
    guye = CharacterState(
        name="古野",
        location="未知",
        emotion="好奇",
        injury="无",
        personality="神秘，知识渊博",
        speech_style="简洁，有哲理"
    )
    tracker.add_character(guye)
    
    # 关系
    tracker.add_relationship(Relationship(
        char1="林风", char2="苏晴", relationship_type="恋人",
        trust_level=90, affinity_level=95
    ))
    tracker.add_relationship(Relationship(
        char1="林风", char2="李磊", relationship_type="兄弟",
        trust_level=95, affinity_level=90
    ))
    tracker.add_relationship(Relationship(
        char1="林风", char2="古野", relationship_type="伙伴",
        trust_level=60, affinity_level=70
    ))
    
    # 初始时间线
    from state_tracker import TimelineEvent
    tracker.add_timeline_event(TimelineEvent(
        day=1, chapter_range="1",
        description="林风从2035年重生回到2010年5月20日",
        key_characters=["林风"]
    ))
    
    # 初始伏笔
    from state_tracker import Foreshadow
    tracker.add_foreshadow(Foreshadow(
        foreshadow_id="f001",
        description="iPhone 15 Pro Max 里有未来15年的所有知识",
        chapter_planted=1
    ))
    
    tracker.save()
    return tracker


def main():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    
    print("=" * 60)
    print("Phase 3 - 增强版逐章生成模块测试")
    print("=" * 60)
    
    # 读取配置
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 创建客户端
    print("\n正在创建客户端...")
    client = OpenAI(
        api_key=config["api_key"],
        base_url=config["base_url"]
    )
    print("客户端创建成功！")
    
    # 初始化状态追踪器
    print("\n正在初始化状态追踪器...")
    tracker = init_test_state_tracker(config)
    print("状态追踪器初始化完成！")
    
    # 输出目录
    output_dir = os.path.join(os.path.dirname(__file__), "data", "output_enhanced")
    os.makedirs(output_dir, exist_ok=True)
    
    # 测试章节大纲（简化版）
    test_outline = {
        "chapter_num": 1,
        "title": "第一章 重生2010",
        "location": "深圳出租屋",
        "characters": ["林风"],
        "core_event": "林风从2035年重生回到2010年5月20日，发现iPhone 15 Pro Max还在身边",
        "dialogue_points": ["内心独白，确认时间"],
        "emotional_tone": "震惊、疑惑、逐渐接受",
        "chapter_hook": "手机屏幕突然亮起，出现一个神秘的AI助手",
        "key_details": ["出租屋是2010年的样子", "iPhone 15 Pro Max是未来的手机", "手机里有未来的照片和信息"]
    }
    
    # 创建生成器
    generator = EnhancedChapterGenerator(client, config, tracker)
    
    # 添加章节摘要到记忆检索器
    # 这里没有之前的章节，所以跳过
    
    # 生成章节
    print("\n" + "=" * 60)
    print("开始生成第1章（增强版）")
    print("=" * 60)
    
    chapter_content, quality = generator.generate_chapter_with_quality(
        chapter_num=1,
        chapter_outline=test_outline,
        previous_chapters=[],
        max_retries=1
    )
    
    # 保存章节
    save_enhanced_chapter(1, chapter_content, quality, output_dir)
    
    # 更新状态追踪器
    tracker.advance_chapter()
    tracker.save()
    
    # 添加章节摘要
    generator.memory_retriever.add_chapter_summary(1, test_outline["core_event"])
    
    # 打印质量报告
    print("\n" + "=" * 60)
    print("质量报告")
    print("=" * 60)
    print(f"整体得分：{quality.overall_score}/10")
    print(f"通过：{'是' if quality.passed else '否'}")
    
    if quality.issues:
        print("\n发现的问题：")
        for issue in quality.issues:
            print(f"  - {issue}")
    
    if quality.suggestions:
        print("\n改进建议：")
        for suggestion in quality.suggestions:
            print(f"  - {suggestion}")
    
    print("\n" + "=" * 60)
    print("Phase 3 测试完成！")
    print(f"结果保存在：{output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
