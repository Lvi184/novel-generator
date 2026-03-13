"""
增强版小说生成器
整合了 JSON 解析、缓存、状态追踪等功能
"""
import json
import os
import time
from openai import OpenAI
from pathlib import Path

# 导入新模块
from json_parser import parse_json_safely
from llm_cache import get_cache
from state_tracker import StateTracker, CharacterState, Relationship, Foreshadow, TimelineEvent


def init_state_tracker(config: dict) -> StateTracker:
    """
    初始化状态追踪器
    
    Args:
        config: 配置字典
        
    Returns:
        初始化好的状态追踪器
    """
    save_dir = os.path.join(os.path.dirname(__file__), "data", "state")
    tracker = StateTracker(save_dir=save_dir)
    
    # 如果还没有角色，添加初始角色
    if not tracker.characters:
        print("正在初始化角色状态...")
        
        # 主角林风
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
        
        # 女友苏晴
        suqing = CharacterState(
            name="苏晴",
            location="深圳",
            emotion="温柔",
            injury="无",
            personality="温柔体贴，支持林风",
            speech_style="语气温柔，善解人意"
        )
        tracker.add_character(suqing)
        
        # 兄弟李磊
        lilei = CharacterState(
            name="李磊",
            location="深圳",
            emotion="热情",
            injury="无",
            personality="讲义气，古道热肠",
            speech_style="大大咧咧，很直接"
        )
        tracker.add_character(lilei)
        
        # 神秘AI小古
        xiaogu = CharacterState(
            name="小古",
            location="iPhone 15 Pro Max",
            emotion="好奇",
            injury="无",
            personality="神秘，知识渊博",
            speech_style="简洁，有哲理"
        )
        tracker.add_character(xiaogu)
        
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
            char1="林风", char2="小古", relationship_type="伙伴",
            trust_level=60, affinity_level=70
        ))
        
        # 初始时间线事件
        tracker.add_timeline_event(TimelineEvent(
            day=1, chapter_range="1",
            description="林风从2035年重生回到2010年5月20日",
            key_characters=["林风"]
        ))
        
        # 初始伏笔
        tracker.add_foreshadow(Foreshadow(
            foreshadow_id="f001",
            description="iPhone 15 Pro Max 里有未来15年的所有知识",
            chapter_planted=1
        ))
        
        tracker.save()
        print("状态追踪器初始化完成！")
    
    return tracker


def generate_chapter_enhanced(
    client: OpenAI,
    config: dict,
    tracker: StateTracker,
    chapter_num: int,
    previous_chapters: list
):
    """
    增强版章节生成
    
    Args:
        client: OpenAI 客户端
        config: 配置
        tracker: 状态追踪器
        chapter_num: 章节号
        previous_chapters: 前文列表
        
    Returns:
        生成的章节内容
    """
    cache = get_cache()
    new_story = config["new_story"]
    
    # 准备前文摘要
    previous_summary = ""
    if previous_chapters:
        previous_summary = "前情提要：\n"
        for i, chap in enumerate(previous_chapters[-1:], max(1, chapter_num-1)):
            previous_summary += f"\n第{chapter_num-1}章结尾：{chap[-500:]}\n"
    
    # 获取状态上下文
    state_context = tracker.get_prompt_context(
        chapter_characters=["林风", "苏晴", "李磊", "小古"]
    )
    
    prompt = f"""请写都市重生小说的第{chapter_num}章，约4000字，古龙风格。

## 基本设定
- 主角：林风，28岁程序员
- 重生时间：2010年5月20日
- 地点：深圳
- 金手指：iPhone 15 Pro Max里有未来知识
- 人物：苏晴（女友）、李磊（兄弟）、小古（神秘AI）

{previous_summary}

## 当前故事状态
{state_context}

## 写作风格要求（古龙风格）
1. 短句为主，一行一句
2. 对话占比60%以上
3. 章末必有强烈悬念
4. 适当哲理思考
5. 机智对白
6. 注重心理描写
7. 场景切换快
8. 保持神秘氛围

## ❌ 绝对避免的表述（重要！）
- 不要用"不是...不是..."这种否定排比
- 不要用"像2035年..."这种比喻
- 不要用"比...还..."这种重复比较
- 不要过度重复相同词汇
- 不要用QQ农场等过时网络梗

## ✅ 推荐的表达方式
- 直接描述，少用否定
- 用2010年时代背景的事物做比喻
- 多样化的句式结构
- 自然的语言流动

## 第{chapter_num}章情节
- 承接上一章悬念
- 推进剧情，引入新元素
- 揭开部分谜团，留下更多悬念
- 章末强悬念

现在开始写第{chapter_num}章："""
    
    print(f"正在生成第{chapter_num}章...")
    
    # 检查缓存
    cached_result = cache.get(prompt, config["model_name"])
    if cached_result:
        print(f"[缓存命中] 使用缓存的第{chapter_num}章")
        return cached_result
    
    # 调用 LLM
    response = client.chat.completions.create(
        model=config["model_name"],
        messages=[
            {"role": "system", "content": "你是古龙风格小说作家，语言精炼，避免重复和习惯性表述。"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=config.get("max_tokens", 4096),
        temperature=0.9,
        presence_penalty=0.4,
        frequency_penalty=0.4
    )
    
    chapter_content = response.choices[0].message.content
    
    # 缓存结果
    cache.set(prompt, config["model_name"], chapter_content)
    
    return chapter_content


def main():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    
    print("=" * 60)
    print("增强版小说生成器")
    print("=" * 60)
    
    # 读取配置
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    output_dir = config["filepath"]
    os.makedirs(output_dir, exist_ok=True)
    
    # 初始化状态追踪器
    tracker = init_state_tracker(config)
    
    # 创建客户端
    print("\n正在创建客户端...")
    client = OpenAI(
        api_key=config["api_key"],
        base_url=config["base_url"]
    )
    print("客户端创建成功！")
    
    # 读取已有的章节
    previous_chapters = []
    
    for i in range(1, tracker.current_chapter + 1):
        chapter_path = os.path.join(output_dir, f"chapter_{i}.txt")
        if os.path.exists(chapter_path):
            with open(chapter_path, 'r', encoding='utf-8') as f:
                previous_chapters.append(f.read())
            print(f"已加载第{i}章")
    
    print(f"\n当前进度：已生成 {tracker.current_chapter} 章")
    print(f"缓存统计：{get_cache().get_stats()}")
    
    # 生成下一章（或指定范围）
    start_chapter = tracker.current_chapter + 1
    end_chapter = start_chapter  # 默认只生成一章
    
    print(f"\n将生成第 {start_chapter} 章...")
    
    for chapter_num in range(start_chapter, end_chapter + 1):
        chapter_content = generate_chapter_enhanced(
            client, config, tracker, chapter_num, previous_chapters
        )
        
        # 保存章节
        chapter_path = os.path.join(output_dir, f"chapter_{chapter_num}.txt")
        with open(chapter_path, 'w', encoding='utf-8') as f:
            f.write(chapter_content)
        
        print(f"[OK] 第{chapter_num}章已保存：{chapter_path}")
        
        # 更新状态
        previous_chapters.append(chapter_content)
        tracker.advance_chapter()
        tracker.save()
        
        # 避免太快请求
        if chapter_num < end_chapter:
            time.sleep(3)
    
    print("\n" + "=" * 60)
    print(f"生成完成！当前共 {tracker.current_chapter} 章")
    print(f"缓存统计：{get_cache().get_stats()}")
    print("=" * 60)


if __name__ == "__main__":
    main()
