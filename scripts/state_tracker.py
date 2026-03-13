"""
状态追踪器
追踪角色状态、关系变化、伏笔、时间线等
"""
import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class CharacterState:
    """角色状态"""
    name: str
    location: str = ""
    emotion: str = "平静"
    injury: str = "无"
    inventory: List[str] = None
    personality: str = ""
    speech_style: str = ""
    
    def __post_init__(self):
        if self.inventory is None:
            self.inventory = []


@dataclass
class Relationship:
    """角色关系"""
    char1: str
    char2: str
    relationship_type: str  # "师徒", "朋友", "敌人", etc.
    trust_level: int = 50  # 0-100
    affinity_level: int = 50  # 0-100
    hostility_level: int = 0  # 0-100
    history: List[str] = None
    
    def __post_init__(self):
        if self.history is None:
            self.history = []


@dataclass
class Foreshadow:
    """伏笔"""
    foreshadow_id: str
    description: str
    chapter_planted: int
    status: str = "planted"  # "planted", "harvested", "abandoned"
    chapter_harvested: Optional[int] = None
    notes: str = ""


@dataclass
class TimelineEvent:
    """时间线事件"""
    day: int
    chapter_range: str
    description: str
    key_characters: List[str] = None
    
    def __post_init__(self):
        if self.key_characters is None:
            self.key_characters = []


@dataclass
class Knowledge:
    """已知信息（谁知道什么）"""
    character: str
    information: str
    knowledge_level: str = "known"  # "known", "unknown", "suspected"
    chapter_learned: Optional[int] = None


class StateTracker:
    """状态追踪器"""
    
    def __init__(self, save_dir: str = "data/state"):
        """
        初始化状态追踪器
        
        Args:
            save_dir: 保存目录
        """
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        # 状态数据
        self.characters: Dict[str, CharacterState] = {}
        self.relationships: List[Relationship] = []
        self.foreshadows: List[Foreshadow] = []
        self.timeline: List[TimelineEvent] = []
        self.knowledges: List[Knowledge] = []
        
        # 当前进度
        self.current_chapter = 0
        self.current_day = 1
        
        # 加载已保存的状态
        self._load()
    
    def _get_save_path(self) -> Path:
        """获取保存文件路径"""
        return self.save_dir / "state.json"
    
    def _load(self) -> None:
        """加载状态"""
        save_path = self._get_save_path()
        if save_path.exists():
            try:
                with open(save_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.current_chapter = data.get('current_chapter', 0)
                self.current_day = data.get('current_day', 1)
                
                # 加载角色
                for char_data in data.get('characters', []):
                    char = CharacterState(**char_data)
                    self.characters[char.name] = char
                
                # 加载关系
                for rel_data in data.get('relationships', []):
                    self.relationships.append(Relationship(**rel_data))
                
                # 加载伏笔
                for foreshadow_data in data.get('foreshadows', []):
                    self.foreshadows.append(Foreshadow(**foreshadow_data))
                
                # 加载时间线
                for event_data in data.get('timeline', []):
                    self.timeline.append(TimelineEvent(**event_data))
                
                # 加载已知信息
                for knowledge_data in data.get('knowledges', []):
                    self.knowledges.append(Knowledge(**knowledge_data))
                
            except Exception as e:
                print(f"[警告] 加载状态失败: {e}")
    
    def save(self) -> None:
        """保存状态"""
        save_path = self._get_save_path()
        
        data = {
            'current_chapter': self.current_chapter,
            'current_day': self.current_day,
            'saved_at': datetime.now().isoformat(),
            'characters': [asdict(char) for char in self.characters.values()],
            'relationships': [asdict(rel) for rel in self.relationships],
            'foreshadows': [asdict(f) for f in self.foreshadows],
            'timeline': [asdict(e) for e in self.timeline],
            'knowledges': [asdict(k) for k in self.knowledges]
        }
        
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[警告] 保存状态失败: {e}")
    
    # === 角色管理 ===
    def add_character(self, character: CharacterState) -> None:
        """添加角色"""
        self.characters[character.name] = character
    
    def get_character(self, name: str) -> Optional[CharacterState]:
        """获取角色"""
        return self.characters.get(name)
    
    def update_character(self, name: str, **kwargs) -> None:
        """更新角色属性"""
        if name in self.characters:
            char = self.characters[name]
            for key, value in kwargs.items():
                if hasattr(char, key):
                    setattr(char, key, value)
    
    # === 关系管理 ===
    def add_relationship(self, relationship: Relationship) -> None:
        """添加关系"""
        self.relationships.append(relationship)
    
    def get_relationship(self, char1: str, char2: str) -> Optional[Relationship]:
        """获取两个角色之间的关系"""
        for rel in self.relationships:
            if (rel.char1 == char1 and rel.char2 == char2) or \
               (rel.char1 == char2 and rel.char2 == char1):
                return rel
        return None
    
    def update_relationship(self, char1: str, char2: str, **kwargs) -> None:
        """更新关系"""
        rel = self.get_relationship(char1, char2)
        if rel:
            for key, value in kwargs.items():
                if hasattr(rel, key):
                    setattr(rel, key, value)
    
    # === 伏笔管理 ===
    def add_foreshadow(self, foreshadow: Foreshadow) -> None:
        """添加伏笔"""
        self.foreshadows.append(foreshadow)
    
    def get_active_foreshadows(self) -> List[Foreshadow]:
        """获取活跃的伏笔（已埋未收）"""
        return [f for f in self.foreshadows if f.status == "planted"]
    
    def harvest_foreshadow(self, foreshadow_id: str, chapter_harvested: int) -> bool:
        """回收伏笔"""
        for f in self.foreshadows:
            if f.foreshadow_id == foreshadow_id:
                f.status = "harvested"
                f.chapter_harvested = chapter_harvested
                return True
        return False
    
    # === 时间线管理 ===
    def add_timeline_event(self, event: TimelineEvent) -> None:
        """添加时间线事件"""
        self.timeline.append(event)
    
    def get_recent_events(self, limit: int = 5) -> List[TimelineEvent]:
        """获取最近的事件"""
        return self.timeline[-limit:]
    
    # === 已知信息管理 ===
    def add_knowledge(self, knowledge: Knowledge) -> None:
        """添加已知信息"""
        self.knowledges.append(knowledge)
    
    def get_character_knowledge(self, character: str) -> List[Knowledge]:
        """获取某个角色的已知信息"""
        return [k for k in self.knowledges if k.character == character]
    
    # === 章节进度 ===
    def advance_chapter(self) -> None:
        """推进一章"""
        self.current_chapter += 1
    
    def advance_day(self, days: int = 1) -> None:
        """推进时间"""
        self.current_day += days
    
    # === 生成提示词 ===
    def get_prompt_context(self, chapter_characters: List[str] = None) -> str:
        """
        生成用于 LLM 的状态上下文
        
        Args:
            chapter_characters: 本章出场的角色列表
            
        Returns:
            状态上下文文本
        """
        context = []
        
        # 角色状态
        context.append("【当前角色状态】")
        chars_to_show = chapter_characters if chapter_characters else list(self.characters.keys())
        for char_name in chars_to_show:
            char = self.characters.get(char_name)
            if char:
                context.append(f"- {char.name}:")
                context.append(f"  位置: {char.location}")
                context.append(f"  情绪: {char.emotion}")
                context.append(f"  伤情: {char.injury}")
                if char.inventory:
                    context.append(f"  持有: {', '.join(char.inventory)}")
                if char.personality:
                    context.append(f"  性格: {char.personality}")
        
        # 活跃伏笔
        active_foreshadows = self.get_active_foreshadows()
        if active_foreshadows:
            context.append("\n【活跃伏笔】")
            for f in active_foreshadows:
                context.append(f"- [第{f.chapter_planted}章] {f.description}")
        
        # 最近事件
        recent_events = self.get_recent_events(3)
        if recent_events:
            context.append("\n【近期事件】")
            for event in recent_events:
                context.append(f"- [第{event.day}天] {event.description}")
        
        return "\n".join(context)
