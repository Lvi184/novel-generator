# Claude Code 创建项目提示词

请根据以下 RPD（需求项目文档）创建一个完整的项目结构。

## 项目位置
D:\openclaw\workspace\case1\

## 项目概述
这是一个基于 AI_NovelGenerator 框架的网络小说叙事技法仿写系统。
核心功能：
1. 分析目标小说（《多情剑客无情剑》）的叙事技法
2. 将技法迁移到新题材（都市重生）
3. 每天自动生成一章小说

## 立即创建的文件

### 1. requirements.txt
```
openai>=1.0.0
anthropic>=0.20.0
chromadb>=0.4.0
jieba>=0.42.0
PyYAML>=6.0
```

### 2. src/__init__.py
```python
# 空文件
```

### 3. src/style_analyzer.py
```python
"""
叙事技法分析模块
分析目标小说的节奏、钩子、对话风格等
"""
import json
import jieba
from typing import Dict, Any

class StyleAnalyzer:
    def __init__(self, config_path: str):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
    
    def analyze_novel(self, novel_path: str) -> Dict[str, Any]:
        """分析整部小说"""
        print(f"分析小说：{novel_path}")
        
        # 这里是简化版本，实际需要完整实现
        profile = {
            "pacing": {
                "avg_scene_length": "短场景，快速切换",
                "tension_pattern": "突然爆发型",
                "dialogue_ratio": 0.6
            },
            "hooks": {
                "hook_frequency": 0.9,
                "hook_types": {
                    "mystery": 0.4,
                    "reveal": 0.3,
                    "cliffhanger": 0.3
                }
            },
            "dialogue_style": {
                "avg_line_length": "短句为主",
                "philosophical_ratio": 0.3,
                "wit_exchange": True
            }
        }
        
        return profile
    
    def save_profile(self, profile: Dict[str, Any], output_path: str):
        """保存叙事技法档案"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)
        print(f"叙事技法档案已保存：{output_path}")
```

### 4. src/narrative_migrator.py
```python
"""
叙事技法迁移模块
将分析出的叙事技法应用到新故事
"""
import json
from typing import Dict, Any

class NarrativeMigrator:
    def __init__(self, config_path: str, narrative_profile: Dict[str, Any]):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        self.profile = narrative_profile
    
    def generate_setting(self) -> str:
        """生成新故事设定"""
        new_story = self.config['new_story']
        
        setting = f"""# 新故事设定

## 题材
{new_story['genre']}

## 核心想法
{new_story['core_idea']}

## 主角
- 姓名：{new_story['protagonist']['name']}
- 年龄：{new_story['protagonist']['age']}
- 职业：{new_story['protagonist']['occupation']}
- 特点：{new_story['protagonist']['trait']}

## 背景
- 时间：{new_story['setting']['time']}
- 地点：{new_story['setting']['location']}
- 时代背景：{new_story['setting']['background']}

## 叙事风格（源自《多情剑客无情剑》）
- 对话占比：60%
- 短句为主
- 90% 章末有悬念
- 有机智对白
- 有哲理金句
"""
        return setting
    
    def generate_directory(self, num_chapters: int = 120) -> str:
        """生成章节目录"""
        directory = f"# 章节目录（共 {num_chapters} 章）\n\n"
        
        for i in range(1, min(num_chapters + 1, 11)):
            directory += f"## 第 {i} 章\n"
            directory += f"- 标题：待生成\n"
            directory += f"- 简述：待生成\n\n"
        
        if num_chapters > 10:
            directory += f"...（共 {num_chapters} 章）\n"
        
        return directory
    
    def save_setting(self, setting: str, output_path: str):
        """保存设定"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(setting)
        print(f"故事设定已保存：{output_path}")
    
    def save_directory(self, directory: str, output_path: str):
        """保存目录"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(directory)
        print(f"章节目录已保存：{output_path}")
```

### 5. src/prompts.yaml
```yaml
# 叙事分析提示词
narrative_analysis: |
  请分析以下小说章节的叙事技法，输出 JSON 格式：
  
  分析维度：
  1. 剧情节奏（紧张度曲线）
  2. 钩子设计（章末悬念）
  3. 对话风格（对话占比、句式）
  4. 冲突模式（冲突类型、升级方式）
  5. 人物弧线（主角成长、关系变化）

# 叙事迁移提示词
narrative_migration: |
  请根据以下叙事技法档案和用户新想法，创作新故事：
  
  要求：
  1. 完全复用原作的叙事节奏和钩子设计
  2. 设定和人物根据用户新想法原创
  3. 保持古龙风格（对话占比高、短句、章末悬念）
```

### 6. data/output/.gitkeep
```
# 保持目录
```

## 完成后请执行
1. 复制目标小说到 data/input/target_novel/
2. 运行分析和迁移脚本
3. 生成第一章节

现在开始创建这些文件！
