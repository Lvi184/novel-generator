"""
Phase 2 - 骨架变形模块
将原著骨架映射到新的世界观和设定
"""
import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional
from openai import OpenAI

from json_parser import parse_json_safely
from llm_cache import get_cache


@dataclass
class WorldMapping:
    """世界观映射"""
    original_element: str
    new_element: str
    mapping_type: str  # "power_system", "geography", "social_structure", "resource", "occupation"
    notes: str = ""


@dataclass
class CharacterMapping:
    """角色映射"""
    original_name: str
    original_role: str
    new_name: str
    new_role: str
    preserve_traits: List[str]  # 保留的性格特征
    replace_traits: Dict[str, str]  # 替换的特征
    notes: str = ""


@dataclass
class BeatMapping:
    """剧情节拍映射"""
    original_beat_id: int
    original_description: str
    new_description: str
    preserve_narrative_function: bool
    notes: str = ""


@dataclass
class TransformedOutline:
    """变形后的新大纲"""
    meta: Dict[str, Any]
    world_mappings: List[WorldMapping]
    character_mappings: List[CharacterMapping]
    beat_mappings: List[BeatMapping]
    chapter_outlines: List[Dict[str, Any]]


class WorldMapper:
    """世界观映射器"""
    
    def __init__(self, client: OpenAI, config: dict):
        self.client = client
        self.config = config
        self.cache = get_cache()
    
    def map_world(self, original_skeleton: Dict[str, Any], new_story: Dict[str, Any]) -> List[WorldMapping]:
        """
        映射世界观
        
        Args:
            original_skeleton: 原著骨架
            new_story: 新故事设定
            
        Returns:
            世界观映射列表
        """
        original_world = original_skeleton.get("world", {})
        new_genre = new_story.get("genre", "")
        new_setting = new_story.get("setting", {})
        
        prompt = f"""请将原著武侠世界观映射到新的都市重生世界观。

## 原著世界观
- 类型：武侠
- 力量体系：{original_world.get('power_system', {}).get('name', '武功体系')}
- 地理：{original_world.get('geography', '江湖')}
- 社会结构：{original_world.get('social_structure', '门派/帮派')}

## 新故事设定
- 类型：{new_genre}
- 背景：{new_setting.get('background', '')}
- 时间：{new_setting.get('time', '')}
- 地点：{new_setting.get('location', '')}

请生成世界观映射，按JSON格式输出：
{{
    "mappings": [
        {{
            "original_element": "原著元素",
            "new_element": "新元素",
            "mapping_type": "power_system|geography|social_structure|resource|occupation",
            "notes": "说明"
        }}
    ]
}}

映射参考：
- 武功/内力 → 编程能力/商业嗅觉
- 江湖/武林 → 互联网圈/商圈
- 门派/帮派 → 科技公司/创业团队
- 武功秘籍 → 未来知识/商业机密
- 炼药师 → AI训练师/投资人
- 神兵利器 → 核心技术/专利

只输出JSON，不要其他文字。"""
        
        print("正在生成世界观映射...")
        
        # 检查缓存
        cached = self.cache.get(prompt, self.config["model_name"], cache_id="world_mapping")
        if cached:
            print("[缓存] 世界观映射")
            mappings_data = cached
        else:
            response = self.client.chat.completions.create(
                model=self.config["model_name"],
                messages=[
                    {"role": "system", "content": "你是专业的世界观设定师。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.5
            )
            
            result, error = parse_json_safely(response.choices[0].message.content)
            if error:
                print(f"[警告] 世界观映射解析失败: {error}")
                return []
            
            mappings_data = result
            self.cache.set(prompt, self.config["model_name"], mappings_data, cache_id="world_mapping")
        
        mappings = []
        for m in mappings_data.get("mappings", []):
            mappings.append(WorldMapping(**m))
        
        print(f"生成了 {len(mappings)} 个世界观映射")
        return mappings


class CharacterMapper:
    """角色映射器"""
    
    def __init__(self, client: OpenAI, config: dict):
        self.client = client
        self.config = config
        self.cache = get_cache()
    
    def map_characters(
        self,
        original_skeleton: Dict[str, Any],
        new_story: Dict[str, Any],
        world_mappings: List[WorldMapping]
    ) -> List[CharacterMapping]:
        """
        映射角色
        
        Args:
            original_skeleton: 原著骨架
            new_story: 新故事设定
            world_mappings: 世界观映射
            
        Returns:
            角色映射列表
        """
        original_chars = original_skeleton.get("characters", [])
        new_protagonist = new_story.get("protagonist", {})
        
        chars_text = "\n".join([
            f"- {c.get('name', '')}: {c.get('narrative_role', '')}, {c.get('personality_core', [])}"
            for c in original_chars[:8]
        ])
        
        prompt = f"""请将原著武侠角色映射到新的都市重生角色。

## 原著角色
{chars_text}

## 新故事主角设定
- 姓名：{new_protagonist.get('name', '')}
- 年龄：{new_protagonist.get('age', '')}
- 职业：{new_protagonist.get('occupation', '')}
- 性格：{new_protagonist.get('trait', '')}

## 映射原则
- 保留叙事功能（主角→主角，导师→导师，反派→反派）
- 保留核心性格特质
- 替换背景设定以符合都市重生题材

请生成角色映射，按JSON格式输出：
{{
    "mappings": [
        {{
            "original_name": "原著角色名",
            "original_role": "原著角色定位",
            "new_name": "新角色名",
            "new_role": "新角色定位",
            "preserve_traits": ["保留的性格1", "保留的性格2"],
            "replace_traits": {{"原著特征": "新特征"}},
            "notes": "说明"
        }}
    ]
}}

映射参考（多情剑客无情剑 → 都市重生）：
- 李寻欢 → 林风（主角，程序员，重情义）
- 阿飞 → 小古（神秘AI/伙伴，孤傲）
- 林诗音 → 苏晴（女友/青梅竹马）
- 龙啸云 → 某商业对手（伪君子）
- 铁传甲 → 李磊（兄弟/忠仆）

只输出JSON，不要其他文字。"""
        
        print("正在生成角色映射...")
        
        # 检查缓存
        cached = self.cache.get(prompt, self.config["model_name"], cache_id="char_mapping")
        if cached:
            print("[缓存] 角色映射")
            mappings_data = cached
        else:
            response = self.client.chat.completions.create(
                model=self.config["model_name"],
                messages=[
                    {"role": "system", "content": "你是专业的角色设定师。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2500,
                temperature=0.5
            )
            
            result, error = parse_json_safely(response.choices[0].message.content)
            if error:
                print(f"[警告] 角色映射解析失败: {error}")
                return []
            
            mappings_data = result
            self.cache.set(prompt, self.config["model_name"], mappings_data, cache_id="char_mapping")
        
        mappings = []
        for m in mappings_data.get("mappings", []):
            mappings.append(CharacterMapping(**m))
        
        print(f"生成了 {len(mappings)} 个角色映射")
        return mappings


class BeatMapper:
    """剧情节拍映射器"""
    
    def __init__(self, client: OpenAI, config: dict):
        self.client = client
        self.config = config
        self.cache = get_cache()
    
    def map_beats(
        self,
        original_skeleton: Dict[str, Any],
        new_story: Dict[str, Any],
        world_mappings: List[WorldMapping],
        character_mappings: List[CharacterMapping]
    ) -> List[BeatMapping]:
        """
        映射剧情节拍
        
        Args:
            original_skeleton: 原著骨架
            new_story: 新故事设定
            world_mappings: 世界观映射
            character_mappings: 角色映射
            
        Returns:
            剧情节拍映射列表
        """
        chars_dict = {m.original_name: m.new_name for m in character_mappings}
        
        prompt = f"""请将原著武侠剧情节拍映射到都市重生题材。

## 原著关键剧情（前20章）
1. 主角关外归来，遇孤独少年
2. 客栈遇袭，少年出手杀人
3. 卷入金丝甲抢夺案
4. 中毒被救
5. 回旧宅，发现旧爱已嫁好友
6. 被构陷成盗匪
7. 少年救人受伤
8. 被押送少林寺

## 新故事设定
- 类型：都市重生
- 背景：2010年深圳互联网创业潮
- 主角：林风（28岁程序员重生）
- 金手指：iPhone 15 Pro Max里的未来知识

## 角色映射
{json.dumps(chars_dict, ensure_ascii=False, indent=2)}

请生成剧情节拍映射，保持叙事功能，替换具体情节：
{{
    "mappings": [
        {{
            "original_beat_id": 1,
            "original_description": "原著剧情描述",
            "new_description": "新剧情描述",
            "preserve_narrative_function": true,
            "notes": "说明"
        }}
    ]
}}

映射参考：
- 关外归来 → 重生回到2010年
- 客栈杀人 → 职场/商场冲突
- 武功比武 → 技术/商业对决
- 金丝甲 → 核心商业机密/未来趋势
- 押送少林 → 商业危机/困境

只输出JSON，不要其他文字。"""
        
        print("正在生成剧情节拍映射...")
        
        # 检查缓存
        cached = self.cache.get(prompt, self.config["model_name"], cache_id="beat_mapping")
        if cached:
            print("[缓存] 剧情节拍映射")
            mappings_data = cached
        else:
            response = self.client.chat.completions.create(
                model=self.config["model_name"],
                messages=[
                    {"role": "system", "content": "你是专业的剧情策划师。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2500,
                temperature=0.6
            )
            
            result, error = parse_json_safely(response.choices[0].message.content)
            if error:
                print(f"[警告] 剧情节拍映射解析失败: {error}")
                return []
            
            mappings_data = result
            self.cache.set(prompt, self.config["model_name"], mappings_data, cache_id="beat_mapping")
        
        mappings = []
        for m in mappings_data.get("mappings", []):
            mappings.append(BeatMapping(**m))
        
        print(f"生成了 {len(mappings)} 个剧情节拍映射")
        return mappings


class OutlineExpander:
    """章节大纲展开器"""
    
    def __init__(self, client: OpenAI, config: dict):
        self.client = client
        self.config = config
        self.cache = get_cache()
    
    def expand_chapter_outlines(
        self,
        beat_mappings: List[BeatMapping],
        character_mappings: List[CharacterMapping],
        num_chapters: int = 20
    ) -> List[Dict[str, Any]]:
        """
        展开章节大纲
        
        Args:
            beat_mappings: 剧情节拍映射
            character_mappings: 角色映射
            num_chapters: 章节数
            
        Returns:
            章节大纲列表
        """
        chars_dict = {m.original_name: m.new_name for m in character_mappings}
        
        prompt = f"""请为都市重生小说生成{num_chapters}章的详细大纲。

## 核心设定
- 主角：林风，28岁程序员，从2035年重生到2010年深圳
- 金手指：iPhone 15 Pro Max里有未来15年的知识
- 风格：古龙风格（短句、高对话占比、悬念）

## 角色
{json.dumps(chars_dict, ensure_ascii=False, indent=2)}

## 参考剧情节拍
{json.dumps([{'original': b.original_description, 'new': b.new_description} for b in beat_mappings[:5]], ensure_ascii=False, indent=2)}

请生成每章的详细大纲，按JSON格式输出：
{{
    "chapters": [
        {{
            "chapter_num": 1,
            "title": "章节标题",
            "location": "场景地点",
            "characters": ["出场角色1", "出场角色2"],
            "core_event": "核心事件",
            "dialogue_points": ["对话要点1", "对话要点2"],
            "emotional_tone": "情感基调",
            "chapter_hook": "章末悬念",
            "key_details": ["关键细节1", "关键细节2"]
        }}
    ]
}}

古龙风格要求：
- 章末必须有强烈悬念
- 对话占比高
- 场景切换快
- 保持神秘氛围

只输出JSON，不要其他文字。"""
        
        print(f"正在生成{num_chapters}章详细大纲...")
        
        # 检查缓存
        cached = self.cache.get(prompt, self.config["model_name"], cache_id=f"outline_{num_chapters}")
        if cached:
            print("[缓存] 章节大纲")
            return cached.get("chapters", [])
        
        response = self.client.chat.completions.create(
            model=self.config["model_name"],
            messages=[
                {"role": "system", "content": "你是专业的小说大纲策划师，擅长古龙风格。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            temperature=0.7
        )
        
        result, error = parse_json_safely(response.choices[0].message.content)
        if error:
            print(f"[警告] 章节大纲解析失败: {error}")
            return []
        
        chapters = result.get("chapters", [])
        self.cache.set(prompt, self.config["model_name"], {"chapters": chapters}, cache_id=f"outline_{num_chapters}")
        
        print(f"生成了 {len(chapters)} 章详细大纲")
        return chapters


class SkeletonTransformer:
    """骨架变形器 - 整合所有映射"""
    
    def __init__(self, client: OpenAI, config: dict):
        self.client = client
        self.config = config
        
        self.world_mapper = WorldMapper(client, config)
        self.character_mapper = CharacterMapper(client, config)
        self.beat_mapper = BeatMapper(client, config)
        self.outline_expander = OutlineExpander(client, config)
    
    def transform(
        self,
        original_skeleton_path: str,
        new_story: Dict[str, Any],
        num_chapters: int = 20
    ) -> TransformedOutline:
        """
        完整的骨架变形流程
        
        Args:
            original_skeleton_path: 原著骨架路径
            new_story: 新故事设定
            num_chapters: 章节数
            
        Returns:
            变形后的新大纲
        """
        print("\n" + "=" * 60)
        print("Phase 2 - 骨架变形")
        print("=" * 60)
        
        # 加载原著骨架
        print("\n正在加载原著骨架...")
        with open(original_skeleton_path, 'r', encoding='utf-8') as f:
            original_skeleton = json.load(f)
        
        # Step 1: 世界观映射
        print("\nStep 1: 世界观映射")
        world_mappings = self.world_mapper.map_world(original_skeleton, new_story)
        
        # Step 2: 角色映射
        print("\nStep 2: 角色映射")
        character_mappings = self.character_mapper.map_characters(
            original_skeleton, new_story, world_mappings
        )
        
        # Step 3: 剧情节拍映射
        print("\nStep 3: 剧情节拍映射")
        beat_mappings = self.beat_mapper.map_beats(
            original_skeleton, new_story, world_mappings, character_mappings
        )
        
        # Step 4: 章节大纲展开
        print("\nStep 4: 章节大纲展开")
        chapter_outlines = self.outline_expander.expand_chapter_outlines(
            beat_mappings, character_mappings, num_chapters
        )
        
        # 构建新大纲
        meta = {
            "original_title": original_skeleton.get("meta", {}).get("original_title", ""),
            "new_genre": new_story.get("genre", ""),
            "num_chapters": num_chapters,
            "transformed_at": "TODO"
        }
        
        outline = TransformedOutline(
            meta=meta,
            world_mappings=world_mappings,
            character_mappings=character_mappings,
            beat_mappings=beat_mappings,
            chapter_outlines=chapter_outlines
        )
        
        print("\n" + "=" * 60)
        print("骨架变形完成！")
        print("=" * 60)
        
        return outline


def save_transformed_outline(outline: TransformedOutline, output_path: str):
    """保存变形后的新大纲"""
    data = {
        "meta": outline.meta,
        "world_mappings": [asdict(m) for m in outline.world_mappings],
        "character_mappings": [asdict(m) for m in outline.character_mappings],
        "beat_mappings": [asdict(m) for m in outline.beat_mappings],
        "chapter_outlines": outline.chapter_outlines
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"新大纲已保存：{output_path}")
