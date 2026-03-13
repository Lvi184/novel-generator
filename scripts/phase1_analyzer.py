"""
Phase 1 - 深度解剖模块
从原著小说中提取结构化骨架
"""
import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from openai import OpenAI

from json_parser import parse_json_safely
from llm_cache import get_cache


@dataclass
class ChapterInfo:
    """章节信息"""
    num: int
    title: str
    content: str


@dataclass
class ChapterSummary:
    """章节摘要"""
    num: int
    title: str
    summary: str
    characters: List[str]
    events: List[str]
    location: str
    tension_level: int  # 1-10


@dataclass
class CharacterProfile:
    """角色档案"""
    id: str
    name: str
    narrative_role: str  # "主角", "配角", "反派", etc.
    archetype: str
    personality_core: List[str]
    character_arc: Dict[str, str]
    function_in_story: str
    speech_style: str
    key_relationships: List[str]


@dataclass
class NovelSkeleton:
    """小说骨架"""
    meta: Dict[str, Any]
    world: Dict[str, Any]
    characters: List[CharacterProfile]
    relationships: List[Dict[str, Any]]
    story_structure: Dict[str, Any]
    rhythm_pattern: Dict[str, Any]
    foreshadowing_patterns: List[Dict[str, Any]]


class NovelSplitter:
    """小说分割器 - 按章节分割"""
    
    def __init__(self, novel_path: str):
        self.novel_path = Path(novel_path)
        self.chapters: List[ChapterInfo] = []
    
    def split_by_chapters(self) -> List[ChapterInfo]:
        """
        按章节分割小说
        
        Returns:
            章节列表
        """
        print(f"正在读取小说：{self.novel_path}")
        
        with open(self.novel_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 尝试多种章节标题格式
        patterns = [
            r'第\s*[零一二三四五六七八九十百千万\d]+\s*章[^\n]*',  # 第X章
            r'Chapter\s*\d+[^\n]*',  # Chapter X
            r'^\s*\d+\s*[-.]\s*[^\n]+',  # 1. 标题
        ]
        
        chapters = []
        current_chapter = None
        
        lines = content.split('\n')
        for line in lines:
            line = line.rstrip()
            
            # 检查是否是章节标题
            is_chapter_title = False
            chapter_title = ""
            
            for pattern in patterns:
                match = re.match(pattern, line.strip())
                if match:
                    is_chapter_title = True
                    chapter_title = match.group(0).strip()
                    break
            
            if is_chapter_title:
                # 保存上一章
                if current_chapter is not None and current_chapter.content.strip():
                    chapters.append(current_chapter)
                
                # 开始新章节
                current_chapter = ChapterInfo(
                    num=len(chapters) + 1,
                    title=chapter_title,
                    content=""
                )
            elif current_chapter is not None:
                current_chapter.content += line + '\n'
        
        # 保存最后一章
        if current_chapter is not None and current_chapter.content.strip():
            chapters.append(current_chapter)
        
        self.chapters = chapters
        print(f"分割完成，共 {len(chapters)} 章")
        
        return chapters


class ChapterSummarizer:
    """章节摘要提取器"""
    
    def __init__(self, client: OpenAI, config: dict):
        self.client = client
        self.config = config
        self.cache = get_cache()
    
    def summarize_chapter(self, chapter: ChapterInfo) -> ChapterSummary:
        """
        摘要单章
        
        Args:
            chapter: 章节信息
            
        Returns:
            章节摘要
        """
        prompt = f"""请分析以下小说章节，提取关键信息。

## 章节标题
{chapter.title}

## 章节内容
{chapter.content[:8000]}  # 限制长度

请按以下JSON格式输出：
{{
    "summary": "本章摘要（300-500字）",
    "characters": ["角色1", "角色2"],
    "events": ["关键事件1", "关键事件2"],
    "location": "场景地点",
    "tension_level": 5  # 紧张度1-10
}}

只输出JSON，不要其他文字。"""
        
        # 检查缓存
        cached = self.cache.get(prompt, self.config["model_name"])
        if cached:
            print(f"[缓存] 第{chapter.num}章摘要")
            return ChapterSummary(
                num=chapter.num,
                title=chapter.title,
                **cached
            )
        
        print(f"正在分析第{chapter.num}章...")
        
        response = self.client.chat.completions.create(
            model=self.config["model_name"],
            messages=[
                {"role": "system", "content": "你是专业的文学分析助手，善于提取小说关键信息。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.3
        )
        
        # 解析结果
        result, error = parse_json_safely(response.choices[0].message.content)
        if error:
            print(f"[警告] 第{chapter.num}章解析失败: {error}")
            result = {
                "summary": "解析失败",
                "characters": [],
                "events": [],
                "location": "",
                "tension_level": 5
            }
        
        # 缓存结果
        self.cache.set(prompt, self.config["model_name"], result)
        
        return ChapterSummary(
            num=chapter.num,
            title=chapter.title,
            **result
        )


class GlobalAnalyzer:
    """全局分析器 - 从章节摘要中提取全局信息"""
    
    def __init__(self, client: OpenAI, config: dict):
        self.client = client
        self.config = config
        self.cache = get_cache()
    
    def analyze_characters(self, summaries: List[ChapterSummary]) -> List[CharacterProfile]:
        """
        分析角色
        
        Args:
            summaries: 章节摘要列表
            
        Returns:
            角色档案列表
        """
        # 合并所有章节的角色
        all_characters = set()
        for summary in summaries:
            all_characters.update(summary.characters)
        
        # 构建角色摘要文本
        summaries_text = "\n".join([
            f"第{s.num}章: {s.summary}\n角色: {', '.join(s.characters)}"
            for s in summaries
        ])
        
        prompt = f"""请基于以下章节摘要，分析小说中的主要角色。

## 章节摘要
{summaries_text}

请为每个主要角色生成档案，按JSON格式输出：
{{
    "characters": [
        {{
            "id": "char_001",
            "name": "角色名",
            "narrative_role": "主角|配角|反派",
            "archetype": "角色原型",
            "personality_core": ["性格1", "性格2"],
            "character_arc": {{
                "start": "开始状态",
                "midpoint": "中期状态",
                "climax": "高潮状态",
                "end": "结局状态"
            }},
            "function_in_story": "叙事功能",
            "speech_style": "说话风格",
            "key_relationships": ["其他角色名"]
        }}
    ]
}}

只输出JSON，不要其他文字。"""
        
        print("正在分析角色...")
        
        response = self.client.chat.completions.create(
            model=self.config["model_name"],
            messages=[
                {"role": "system", "content": "你是专业的文学分析助手。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=3000,
            temperature=0.3
        )
        
        result, error = parse_json_safely(response.choices[0].message.content)
        if error:
            print(f"[警告] 角色分析失败: {error}")
            return []
        
        characters = []
        for char_data in result.get("characters", []):
            characters.append(CharacterProfile(**char_data))
        
        return characters
    
    def build_skeleton(self, chapters: List[ChapterInfo], summaries: List[ChapterSummary]) -> NovelSkeleton:
        """
        构建完整小说骨架
        
        Args:
            chapters: 原始章节
            summaries: 章节摘要
            
        Returns:
            小说骨架
        """
        # 先分析角色
        characters = self.analyze_characters(summaries)
        
        # 构建骨架（简化版）
        skeleton = NovelSkeleton(
            meta={
                "original_title": chapters[0].title if chapters else "Unknown",
                "genre": "武侠",
                "theme": ["江湖", "情义"],
                "total_chapters": len(chapters),
                "core_appeal": "武侠小说的核心魅力"
            },
            world={
                "power_system": {"name": "武功体系", "levels": []},
                "geography": "江湖",
                "social_structure": "门派/帮派"
            },
            characters=characters,
            relationships=[],
            story_structure={
                "type": "传统武侠",
                "acts": [],
                "plot_beats": []
            },
            rhythm_pattern={
                "cycle": "章节循环",
                "cycle_template": [],
                "tension_curve_shape": "波动上升"
            },
            foreshadowing_patterns=[]
        )
        
        return skeleton


class RecursiveSummarizer:
    """递归摘要系统 - 用于处理长篇小说"""
    
    def __init__(self, client: OpenAI, config: dict):
        self.client = client
        self.config = config
        self.cache = get_cache()
    
    def summarize_group(self, summaries: List[ChapterSummary], group_name: str, level: int) -> str:
        """
        摘要一组章节
        
        Args:
            summaries: 章节摘要列表
            group_name: 组名
            level: 层级（Level 1=章，Level 2=组，Level 3=大组...）
            
        Returns:
            组摘要
        """
        summaries_text = "\n".join([
            f"第{s.num}章 ({s.title}):\n{s.summary}\n"
            for s in summaries
        ])
        
        prompt = f"""请为以下{len(summaries)}章小说生成一个综合摘要。

## 章节摘要
{summaries_text}

请生成这{len(summaries)}章的综合摘要（300-500字），包括：
1. 这几章的主要剧情发展
2. 关键角色的表现
3. 重要的转折和伏笔

只输出摘要文本，不要其他格式。"""
        
        cache_key = f"recursive_{level}_{group_name}"
        cached = self.cache.get(prompt, self.config["model_name"], cache_id=cache_key)
        if cached:
            return cached
        
        print(f"正在生成 {group_name} 摘要 (Level {level})...")
        
        response = self.client.chat.completions.create(
            model=self.config["model_name"],
            messages=[
                {"role": "system", "content": "你是专业的文学摘要助手。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.3
        )
        
        result = response.choices[0].message.content.strip()
        self.cache.set(prompt, self.config["model_name"], result, cache_id=cache_key)
        
        return result
    
    def build_recursive_summary(
        self,
        summaries: List[ChapterSummary],
        group_size: int = 10,
        max_level: int = 3
    ) -> Dict[str, Any]:
        """
        构建递归摘要金字塔
        
        Args:
            summaries: 所有章节摘要
            group_size: 每组章节数
            max_level: 最大层级
            
        Returns:
            递归摘要数据结构
        """
        print("\n" + "=" * 60)
        print("构建递归摘要金字塔")
        print("=" * 60)
        
        result = {
            "level_1": [  # 原始章节摘要
                {
                    "num": s.num,
                    "title": s.title,
                    "summary": s.summary,
                    "characters": s.characters,
                    "tension_level": s.tension_level
                }
                for s in summaries
            ],
            "level_2": [],  # 组摘要
            "level_3": [],  # 大组摘要
            "full_summary": ""
        }
        
        # Level 2: 分组摘要
        current_level = 2
        level_summaries = []
        
        for i in range(0, len(summaries), group_size):
            group = summaries[i:i + group_size]
            start_chapter = group[0].num
            end_chapter = group[-1].num
            group_name = f"第{start_chapter}-{end_chapter}章"
            
            group_summary = self.summarize_group(group, group_name, current_level)
            level_summaries.append({
                "group_name": group_name,
                "start_chapter": start_chapter,
                "end_chapter": end_chapter,
                "summary": group_summary
            })
        
        result["level_2"] = level_summaries
        print(f"Level 2 完成：{len(level_summaries)} 个组")
        
        # Level 3: 大组摘要（如果需要）
        if max_level >= 3 and len(level_summaries) > 1:
            current_level = 3
            
            # 将 Level 2 的摘要包装成虚拟章节
            virtual_chapters = []
            for idx, ls in enumerate(level_summaries):
                virtual_chapters.append(ChapterSummary(
                    num=idx + 1,
                    title=ls["group_name"],
                    summary=ls["summary"],
                    characters=[],
                    events=[],
                    location="",
                    tension_level=5
                ))
            
            # 递归生成 Level 3
            for i in range(0, len(virtual_chapters), group_size):
                group = virtual_chapters[i:i + group_size]
                group_name = f"大组{i//group_size + 1}"
                
                group_summary = self.summarize_group(group, group_name, current_level)
                result["level_3"].append({
                    "group_name": group_name,
                    "summary": group_summary
                })
            
            print(f"Level 3 完成：{len(result['level_3'])} 个大组")
        
        # 生成全书摘要
        if result["level_3"]:
            all_summaries = "\n".join([g["summary"] for g in result["level_3"]])
        else:
            all_summaries = "\n".join([g["summary"] for g in result["level_2"]])
        
        final_prompt = f"""基于以下章节组摘要，生成全书的综合摘要（500-800字）。

## 组摘要
{all_summaries}

请生成全书摘要，包括：
1. 整体故事概述
2. 主要角色介绍
3. 核心冲突和主题
4. 故事结构特点

只输出摘要文本。"""
        
        print("\n正在生成全书摘要...")
        response = self.client.chat.completions.create(
            model=self.config["model_name"],
            messages=[
                {"role": "system", "content": "你是专业的文学分析助手。"},
                {"role": "user", "content": final_prompt}
            ],
            max_tokens=1500,
            temperature=0.3
        )
        
        result["full_summary"] = response.choices[0].message.content.strip()
        print("全书摘要完成！")
        
        return result


def save_skeleton(skeleton: NovelSkeleton, output_path: str):
    """保存小说骨架"""
    data = {
        "meta": skeleton.meta,
        "world": skeleton.world,
        "characters": [asdict(c) for c in skeleton.characters],
        "relationships": skeleton.relationships,
        "story_structure": skeleton.story_structure,
        "rhythm_pattern": skeleton.rhythm_pattern,
        "foreshadowing_patterns": skeleton.foreshadowing_patterns
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"骨架已保存：{output_path}")


def save_recursive_summary(recursive_data: Dict[str, Any], output_path: str):
    """保存递归摘要"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(recursive_data, f, ensure_ascii=False, indent=2)
    
    print(f"递归摘要已保存：{output_path}")
