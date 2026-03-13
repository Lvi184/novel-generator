"""
Prompt 模板管理模块
集中管理所有 Prompt 模板，方便调优而不改代码
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class PromptTemplate:
    """Prompt 模板"""
    
    def __init__(self, name: str, template: str, description: str = ""):
        self.name = name
        self.template = template
        self.description = description
    
    def format(self, **kwargs) -> str:
        """格式化模板"""
        return self.template.format(**kwargs)


class PromptManager:
    """Prompt 管理器"""
    
    def __init__(self, templates_dir: str = "prompts"):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.templates: Dict[str, PromptTemplate] = {}
        self._load_builtin_templates()
    
    def _load_builtin_templates(self):
        """加载内置模板"""
        
        # === Phase 1 模板 ===
        
        # 逐章摘要
        self.templates["chapter_summary"] = PromptTemplate(
            name="chapter_summary",
            description="逐章摘要提取",
            template="""请分析以下小说章节，提取关键信息。

## 章节标题
{title}

## 章节内容
{content}

请按以下JSON格式输出：
{{
    "summary": "本章摘要（300-500字）",
    "characters": ["角色1", "角色2"],
    "events": ["关键事件1", "关键事件2"],
    "location": "场景地点",
    "tension_level": 5
}}

只输出JSON，不要其他文字。"""
        )
        
        # 全局角色分析
        self.templates["character_analysis"] = PromptTemplate(
            name="character_analysis",
            description="全局角色分析",
            template="""请基于以下章节摘要，分析小说中的主要角色。

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
        )
        
        # 递归组摘要
        self.templates["group_summary"] = PromptTemplate(
            name="group_summary",
            description="一组章节的综合摘要",
            template="""请为以下{num_chapters}章小说生成一个综合摘要。

## 章节摘要
{summaries_text}

请生成这{num_chapters}章的综合摘要（300-500字），包括：
1. 这几章的主要剧情发展
2. 关键角色的表现
3. 重要的转折和伏笔

只输出摘要文本，不要其他格式。"""
        )
        
        # 全书摘要
        self.templates["full_summary"] = PromptTemplate(
            name="full_summary",
            description="全书综合摘要",
            template="""基于以下章节组摘要，生成全书的综合摘要（500-800字）。

## 组摘要
{all_summaries}

请生成全书摘要，包括：
1. 整体故事概述
2. 主要角色介绍
3. 核心冲突和主题
4. 故事结构特点

只输出摘要文本。"""
        )
        
        # === Phase 2 模板 ===
        
        # 世界观映射
        self.templates["world_mapping"] = PromptTemplate(
            name="world_mapping",
            description="世界观映射",
            template="""请将原著武侠世界观映射到新的都市重生世界观。

## 原著世界观
- 类型：武侠
- 力量体系：{power_system}
- 地理：{geography}
- 社会结构：{social_structure}

## 新故事设定
- 类型：{new_genre}
- 背景：{background}
- 时间：{time}
- 地点：{location}

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

只输出JSON，不要其他文字。"""
        )
        
        # 角色映射
        self.templates["character_mapping"] = PromptTemplate(
            name="character_mapping",
            description="角色映射",
            template="""请将原著武侠角色映射到新的都市重生角色。

## 原著角色
{chars_text}

## 新故事主角设定
- 姓名：{protagonist_name}
- 年龄：{protagonist_age}
- 职业：{protagonist_occupation}
- 性格：{protagonist_trait}

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

只输出JSON，不要其他文字。"""
        )
        
        # 剧情节拍映射
        self.templates["beat_mapping"] = PromptTemplate(
            name="beat_mapping",
            description="剧情节拍映射",
            template="""请将原著武侠剧情节拍映射到都市重生题材。

## 原著关键剧情（前20章）
{original_beats}

## 新故事设定
- 类型：都市重生
- 背景：2010年深圳互联网创业潮
- 主角：{protagonist_name}（{protagonist_age}岁程序员重生）
- 金手指：iPhone 15 Pro Max里的未来知识

## 角色映射
{chars_dict}

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

只输出JSON，不要其他文字。"""
        )
        
        # 章节大纲展开
        self.templates["chapter_outline"] = PromptTemplate(
            name="chapter_outline",
            description="章节大纲展开",
            template="""请为都市重生小说生成{num_chapters}章的详细大纲。

## 核心设定
- 主角：{protagonist_name}，{protagonist_age}岁程序员，从2035年重生到2010年{location}
- 金手指：iPhone 15 Pro Max里有未来15年的知识
- 风格：古龙风格（短句、高对话占比、悬念）

## 角色
{chars_dict_text}

## 参考剧情节拍
{beats_text}

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
        )
        
        # === Phase 3 模板 ===
        
        # 章节生成
        self.templates["chapter_generation"] = PromptTemplate(
            name="chapter_generation",
            description="章节生成",
            template="""请写都市重生小说的第{chapter_num}章，约4000字，古龙风格。

## 基本设定
- 主角：{protagonist_name}，{protagonist_age}岁程序员
- 重生时间：2010年5月20日
- 地点：{location}
- 金手指：iPhone 15 Pro Max里有未来知识
- 人物：{characters_text}

{previous_summary}

## 相关记忆
{memories_text}

## 本章大纲
- 标题：{title}
- 场景：{location_outline}
- 角色：{characters_outline}
- 核心事件：{core_event}
- 情感基调：{emotional_tone}
- 章末悬念：{chapter_hook}

## 写作风格要求（古龙风格）
1. 短句为主，一行一句
2. 对话占比60%以上
3. 章末必有强烈悬念
4. 适当哲理思考
5. 机智对白
6. 注重心理描写
7. 场景切换快
8. 保持神秘氛围

{improvement_text}

现在开始写第{chapter_num}章："""
        )
        
        # 质量检查
        self.templates["quality_check"] = PromptTemplate(
            name="quality_check",
            description="章节质量检查",
            template="""请检查以下小说章节的质量，按JSON格式输出结果。

## 章节大纲
{outline_json}

## 章节内容
{chapter_content}

{previous_chapter_text}

## 检查项目
1. 内容是否符合大纲？
2. 角色言行是否符合人设？
3. 有没有和前文矛盾？
4. 古龙风格是否达标？（短句、高对话占比、悬念）
5. 有没有重复或啰嗦的内容？
6. 章末悬念是否足够强？

请按JSON格式输出：
{{
    "passed": true/false,
    "issues": ["问题1", "问题2"],
    "suggestions": ["建议1", "建议2"],
    "overall_score": 7
}}

评分标准：
- 9-10分：完美，直接可用
- 7-8分： minor问题，微调即可
- 5-6分：较多问题，需要修改
- 1-4分：严重问题，建议重写

只输出JSON，不要其他文字。"""
        )
        
        # 衔接优化
        self.templates["transition_optimize"] = PromptTemplate(
            name="transition_optimize",
            description="章节衔接优化",
            template="""请检查两章之间的衔接是否自然，并提出改进建议。

## 上一章结尾
{previous_end}

## 本章开头
{current_start}

## 本章大纲
{outline_json}

请检查：
1. 场景衔接是否自然？
2. 时间线是否连续？
3. 角色状态是否一致？
4. 情绪基调是否连贯？

请按JSON格式输出：
{{
    "coherent": true/false,
    "issues": ["问题1", "问题2"],
    "improved_opening": "改进后的本章开头（200-300字），或null表示不需要"
}}

只输出JSON，不要其他文字。"""
        )
    
    def get(self, name: str) -> PromptTemplate:
        """获取模板"""
        return self.templates.get(name)
    
    def format(self, name: str, **kwargs) -> str:
        """获取并格式化模板"""
        template = self.templates.get(name)
        if template:
            return template.format(**kwargs)
        return ""
    
    def save_to_file(self, name: str, file_path: str = None):
        """保存模板到文件"""
        if name not in self.templates:
            return
        
        template = self.templates[name]
        if file_path is None:
            file_path = self.templates_dir / f"{name}.txt"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# {template.name}\n\n")
            if template.description:
                f.write(f"## 描述\n{template.description}\n\n")
            f.write(f"## 模板\n{template.template}\n")
    
    def load_from_file(self, name: str, file_path: str = None) -> bool:
        """从文件加载模板"""
        if file_path is None:
            file_path = self.templates_dir / f"{name}.txt"
        
        if not os.path.exists(file_path):
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 简单解析：从 ## 模板 之后的内容
        template_start = content.find("## 模板")
        if template_start == -1:
            return False
        
        template_text = content[template_start + len("## 模板"):].strip()
        
        if name in self.templates:
            self.templates[name].template = template_text
        else:
            self.templates[name] = PromptTemplate(name, template_text)
        
        return True
    
    def list_templates(self) -> list:
        """列出所有模板"""
        return list(self.templates.keys())


# 全局实例
_global_prompt_manager: Optional[PromptManager] = None


def get_prompt_manager() -> PromptManager:
    """获取全局 Prompt 管理器"""
    global _global_prompt_manager
    if _global_prompt_manager is None:
        _global_prompt_manager = PromptManager()
    return _global_prompt_manager


def set_prompt_manager(manager: PromptManager) -> None:
    """设置全局 Prompt 管理器"""
    global _global_prompt_manager
    _global_prompt_manager = manager
