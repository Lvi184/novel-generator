"""
Phase 3 - 增强版逐章生成模块
包含记忆系统、质量检查、自动重试、章节衔接优化
"""
import json
import os
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from openai import OpenAI

from json_parser import parse_json_safely
from llm_cache import get_cache
from state_tracker import StateTracker, CharacterState


@dataclass
class ChapterQuality:
    """章节质量检查结果"""
    passed: bool
    issues: List[str]
    suggestions: List[str]
    overall_score: int  # 1-10


@dataclass
class ChapterTransition:
    """章节衔接检查结果"""
    coherent: bool
    issues: List[str]
    improved_opening: Optional[str]


class MemoryRetriever:
    """记忆检索器 - 基于关键词的记忆检索"""
    
    def __init__(self, state_tracker: StateTracker):
        self.state_tracker = state_tracker
        self.chapter_summaries: Dict[int, str] = {}
    
    def add_chapter_summary(self, chapter_num: int, summary: str):
        """添加章节摘要"""
        self.chapter_summaries[chapter_num] = summary
    
    def retrieve_relevant_memories(
        self,
        current_chapter_outline: Dict[str, Any],
        top_k: int = 3
    ) -> List[str]:
        """
        检索相关记忆
        
        Args:
            current_chapter_outline: 当前章节大纲
            top_k: 返回记忆数量
            
        Returns:
            相关记忆列表
        """
        memories = []
        
        # 提取当前章节关键词
        chapter_chars = current_chapter_outline.get("characters", [])
        chapter_location = current_chapter_outline.get("location", "")
        chapter_event = current_chapter_outline.get("core_event", "")
        
        # 1. 获取角色状态
        for char_name in chapter_chars:
            char = self.state_tracker.get_character(char_name)
            if char:
                memories.append(f"【角色状态】{char.name}：位置={char.location}，情绪={char.emotion}，伤情={char.injury}")
                if char.inventory:
                    memories.append(f"【持有物品】{char.name}：{', '.join(char.inventory)}")
        
        # 2. 获取活跃伏笔
        active_foreshadows = self.state_tracker.get_active_foreshadows()
        for f in active_foreshadows[:3]:
            memories.append(f"【伏笔】第{f.chapter_planted}章：{f.description}")
        
        # 3. 获取最近章节摘要
        recent_chapters = sorted(self.chapter_summaries.keys(), reverse=True)[:3]
        for chap_num in recent_chapters:
            if chap_num in self.chapter_summaries:
                memories.append(f"【前情】第{chap_num}章：{self.chapter_summaries[chap_num][:200]}...")
        
        # 4. 获取角色关系
        for char1 in chapter_chars:
            for char2 in chapter_chars:
                if char1 != char2:
                    rel = self.state_tracker.get_relationship(char1, char2)
                    if rel:
                        memories.append(f"【关系】{char1} & {char2}：{rel.relationship_type}，信任度={rel.trust_level}")
        
        return memories[:top_k * 2]


class QualityChecker:
    """质量检查器"""
    
    def __init__(self, client: OpenAI, config: dict):
        self.client = client
        self.config = config
        self.cache = get_cache()
    
    def check_chapter(
        self,
        chapter_content: str,
        chapter_outline: Dict[str, Any],
        previous_chapter: Optional[str] = None
    ) -> ChapterQuality:
        """
        检查章节质量
        
        Args:
            chapter_content: 章节内容
            chapter_outline: 章节大纲
            previous_chapter: 上一章内容
            
        Returns:
            质量检查结果
        """
        prompt = f"""请检查以下小说章节的质量，按JSON格式输出结果。

## 章节大纲
{json.dumps(chapter_outline, ensure_ascii=False, indent=2)}

## 章节内容
{chapter_content[:6000]}  # 限制长度

{f"## 上一章结尾\n{previous_chapter[-1000:] if previous_chapter else ''}" if previous_chapter else ""}

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
        
        print("正在检查章节质量...")
        
        response = self.client.chat.completions.create(
            model=self.config["model_name"],
            messages=[
                {"role": "system", "content": "你是专业的小说编辑和质量检查员。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.3
        )
        
        result, error = parse_json_safely(response.choices[0].message.content)
        if error:
            print(f"[警告] 质量检查解析失败: {error}")
            return ChapterQuality(
                passed=True,
                issues=[],
                suggestions=["质量检查暂时不可用"],
                overall_score=7
            )
        
        return ChapterQuality(
            passed=result.get("passed", True),
            issues=result.get("issues", []),
            suggestions=result.get("suggestions", []),
            overall_score=result.get("overall_score", 7)
        )


class TransitionOptimizer:
    """章节衔接优化器"""
    
    def __init__(self, client: OpenAI, config: dict):
        self.client = client
        self.config = config
        self.cache = get_cache()
    
    def optimize_transition(
        self,
        previous_chapter: str,
        current_chapter: str,
        current_outline: Dict[str, Any]
    ) -> ChapterTransition:
        """
        优化章节衔接
        
        Args:
            previous_chapter: 上一章内容
            current_chapter: 当前章节内容
            current_outline: 当前章节大纲
            
        Returns:
            衔接检查结果
        """
        prompt = f"""请检查两章之间的衔接是否自然，并提出改进建议。

## 上一章结尾
{previous_chapter[-1500:]}

## 本章开头
{current_chapter[:1500]}

## 本章大纲
{json.dumps(current_outline, ensure_ascii=False, indent=2)}

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
        
        print("正在检查章节衔接...")
        
        response = self.client.chat.completions.create(
            model=self.config["model_name"],
            messages=[
                {"role": "system", "content": "你是专业的小说编辑，擅长章节衔接优化。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.4
        )
        
        result, error = parse_json_safely(response.choices[0].message.content)
        if error:
            print(f"[警告] 衔接检查解析失败: {error}")
            return ChapterTransition(
                coherent=True,
                issues=[],
                improved_opening=None
            )
        
        improved = result.get("improved_opening")
        if improved == "null" or improved == "":
            improved = None
        
        return ChapterTransition(
            coherent=result.get("coherent", True),
            issues=result.get("issues", []),
            improved_opening=improved
        )


class EnhancedChapterGenerator:
    """增强版章节生成器"""
    
    def __init__(self, client: OpenAI, config: dict, state_tracker: StateTracker):
        self.client = client
        self.config = config
        self.state_tracker = state_tracker
        
        self.memory_retriever = MemoryRetriever(state_tracker)
        self.quality_checker = QualityChecker(client, config)
        self.transition_optimizer = TransitionOptimizer(client, config)
        self.cache = get_cache()
    
    def generate_chapter_with_quality(
        self,
        chapter_num: int,
        chapter_outline: Dict[str, Any],
        previous_chapters: List[str],
        max_retries: int = 2
    ) -> Tuple[str, ChapterQuality]:
        """
        生成章节并进行质量检查（含自动重试）
        
        Args:
            chapter_num: 章节号
            chapter_outline: 章节大纲
            previous_chapters: 前文列表
            max_retries: 最大重试次数
            
        Returns:
            (章节内容, 质量检查结果)
        """
        chapter_content = None
        quality = None
        
        for attempt in range(max_retries + 1):
            # 生成章节
            chapter_content = self._generate_chapter(
                chapter_num, chapter_outline, previous_chapters,
                quality if attempt > 0 else None
            )
            
            # 质量检查
            previous_chapter = previous_chapters[-1] if previous_chapters else None
            quality = self.quality_checker.check_chapter(
                chapter_content, chapter_outline, previous_chapter
            )
            
            print(f"第{chapter_num}章 - 尝试 {attempt + 1}/{max_retries + 1}，得分：{quality.overall_score}/10")
            
            if quality.passed and quality.overall_score >= 7:
                print("[OK] 质量达标！")
                break
            elif attempt < max_retries:
                print("[WARN] 需要改进，问题：{quality.issues}")
                print(f"  建议：{quality.suggestions}")
                time.sleep(2)
        
        # 优化衔接（如果不是第一章）
        if chapter_num > 1 and previous_chapters:
            transition = self.transition_optimizer.optimize_transition(
                previous_chapters[-1], chapter_content, chapter_outline
            )
            
            if not transition.coherent:
                print(f"衔接问题：{transition.issues}")
            
            if transition.improved_opening:
                print("应用改进后的开头...")
                # 替换开头
                lines = chapter_content.split('\n')
                # 找到第一个空行或合适的位置替换
                for i, line in enumerate(lines[:20]):
                    if line.strip() == "":
                        break
                # 用改进的开头替换前i行
                chapter_content = transition.improved_opening + '\n' + '\n'.join(lines[i:])
        
        return chapter_content, quality
    
    def _generate_chapter(
        self,
        chapter_num: int,
        chapter_outline: Dict[str, Any],
        previous_chapters: List[str],
        previous_quality: Optional[ChapterQuality] = None
    ) -> str:
        """生成单章（内部方法）"""
        
        # 检索相关记忆
        memories = self.memory_retriever.retrieve_relevant_memories(chapter_outline)
        
        # 准备前文摘要
        previous_summary = ""
        if previous_chapters:
            previous_summary = "前情提要：\n"
            previous_summary += f"\n第{chapter_num-1}章结尾：{previous_chapters[-1][-500:]}\n"
        
        # 构建提示词
        prompt_parts = [
            f"请写都市重生小说的第{chapter_num}章，约4000字，古龙风格。\n",
            "## 基本设定\n",
            "- 主角：林风，28岁程序员\n",
            "- 重生时间：2010年5月20日\n",
            "- 地点：深圳\n",
            "- 金手指：iPhone 15 Pro Max里有未来知识\n",
            "- 人物：苏晴（女友）、李磊（兄弟）、古野（神秘黑客）、龙海（反派）\n",
            "\n",
            previous_summary,
            "\n## 相关记忆\n",
        ]
        
        for memory in memories:
            prompt_parts.append(f"- {memory}\n")
        
        prompt_parts.extend([
            "\n## 本章大纲\n",
            f"- 标题：{chapter_outline.get('title', '')}\n",
            f"- 场景：{chapter_outline.get('location', '')}\n",
            f"- 角色：{', '.join(chapter_outline.get('characters', []))}\n",
            f"- 核心事件：{chapter_outline.get('core_event', '')}\n",
            f"- 情感基调：{chapter_outline.get('emotional_tone', '')}\n",
            f"- 章末悬念：{chapter_outline.get('chapter_hook', '')}\n",
            "\n## 写作风格要求（古龙风格）\n",
            "1. 短句为主，一行一句\n",
            "2. 对话占比60%以上\n",
            "3. 章末必有强烈悬念\n",
            "4. 适当哲理思考\n",
            "5. 机智对白\n",
            "6. 注重心理描写\n",
            "7. 场景切换快\n",
            "8. 保持神秘氛围\n",
        ])
        
        if previous_quality and previous_quality.issues:
            prompt_parts.extend([
                "\n## 需要改进的问题（上次生成的问题）\n",
            ])
            for issue in previous_quality.issues:
                prompt_parts.append(f"- {issue}\n")
            
            if previous_quality.suggestions:
                prompt_parts.extend([
                    "\n## 改进建议\n",
                ])
                for suggestion in previous_quality.suggestions:
                    prompt_parts.append(f"- {suggestion}\n")
        
        prompt_parts.append(f"\n现在开始写第{chapter_num}章：")
        
        prompt = "".join(prompt_parts)
        
        # 检查缓存
        cache_key = f"enhanced_chapter_{chapter_num}"
        cached = self.cache.get(prompt, self.config["model_name"], cache_id=cache_key)
        if cached:
            print(f"[缓存] 第{chapter_num}章")
            return cached
        
        print(f"正在生成第{chapter_num}章...")
        
        response = self.client.chat.completions.create(
            model=self.config["model_name"],
            messages=[
                {"role": "system", "content": "你是古龙风格小说作家，语言精炼，避免重复。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=self.config.get("max_tokens", 4096),
            temperature=0.9,
            presence_penalty=0.4,
            frequency_penalty=0.4
        )
        
        chapter_content = response.choices[0].message.content
        
        # 缓存结果
        self.cache.set(prompt, self.config["model_name"], chapter_content, cache_id=cache_key)
        
        return chapter_content


def save_enhanced_chapter(
    chapter_num: int,
    content: str,
    quality: ChapterQuality,
    output_dir: str
):
    """保存增强版章节"""
    # 保存正文
    chapter_path = os.path.join(output_dir, f"chapter_{chapter_num}.txt")
    with open(chapter_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 保存质量报告
    quality_path = os.path.join(output_dir, f"chapter_{chapter_num}_quality.json")
    quality_data = asdict(quality)
    with open(quality_path, 'w', encoding='utf-8') as f:
        json.dump(quality_data, f, ensure_ascii=False, indent=2)
    
    print(f"第{chapter_num}章已保存，质量得分：{quality.overall_score}/10")
